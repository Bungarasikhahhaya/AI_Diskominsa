import os
import glob
import re
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(__file__))
CSV_DIR = os.path.join(ROOT, "data", "csv")

CATALOG_URL_MAP = None

METRIC_PRIORITY = [
    "disabilitas",
    "cacat",
    "penderita",
    "gini",
    "inflasi",
    "pengeluaran",
    "perkapita",
    "penduduk",
    "populasi",
]

METRIC_SYNONYMS = {
    "disabilitas": "cacat",
    "penyandang": "cacat",
}

METRIC_COLUMN_PATTERNS = {
    "cacat": ["jumlah_penderita_cacat", "jumlah_cacat", "penderita_cacat", "cacat"],
    "disabilitas": ["disabilitas"],
    "penderita": ["jumlah_penderita", "penderita"],
    "gini": ["gini", "rasio_gini", "gini_rasio"],
    "inflasi": ["inflasi"],
    "pengeluaran": ["pengeluaran", "belanja", "biaya"],
    "perkapita": ["perkapita", "per_kapita"],
    "penduduk": ["jumlah_penduduk", "penduduk", "populasi"],
    "populasi": ["populasi", "jumlah_populasi"],
}

REGION_COLUMN_PATTERNS = [
    "bps_nama_kabupaten_kota",
    "bps_nama_provinsi",
    "bps_nama_kecamatan",
    "kemendagri_nama_kabupaten_kota",
    "kemendagri_nama_provinsi",
    "kabupaten_kota",
    "kabupaten",
    "kota",
    "nama_kabupaten",
    "nama_kota",
    "nama_provinsi",
    "provinsi",
    "desa",
    "kecamatan",
]

YEAR_COLUMN_PATTERNS = ["tahun", "year", "periode", "bulan", "month"]

COMMON_QUESTION_TOKENS = {
    "berapa",
    "apa",
    "adalah",
    "jumlah",
    "data",
    "yang",
    "di",
    "ke",
    "dari",
    "untuk",
    "pada",
    "tahun",
    "kabupaten",
    "kota",
    "provinsi",
    "aceh",
    "menurut",
    "bulan",
}

FILE_INDEX = None


def _normalize_text(text):
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()


def _normalize_for_filename(text):
    return re.sub(r"[^a-z0-9]+", "", str(text).lower()).strip()


def _build_catalog_url_map():
    global CATALOG_URL_MAP
    if CATALOG_URL_MAP is not None:
        return CATALOG_URL_MAP

    try:
        from services.catalog import get_catalog

        catalog = get_catalog()
    except Exception:
        catalog = []

    mapping = {}
    for dataset in catalog:
        title = dataset.get("title") or ""
        url = (
            dataset.get("landingPage")
            or (dataset.get("distribution") or [{}])[0].get("accessURL")
            or dataset.get("url")
            or dataset.get("link")
            or dataset.get("dataset_url")
            or ""
        )
        if not title or not url:
            continue
        key = _normalize_for_filename(title)
        if key:
            mapping[key] = url

    CATALOG_URL_MAP = mapping
    return CATALOG_URL_MAP


def _get_dataset_url_for_csv_path(path):
    filename = os.path.splitext(os.path.basename(path))[0]
    normalized = _normalize_for_filename(filename)
    if normalized.startswith("_"):
        normalized = normalized[1:]

    catalog_map = _build_catalog_url_map()
    if normalized in catalog_map:
        return catalog_map[normalized]

    return None


def _tokens(text):
    tokens = re.findall(r"\w+", str(text).lower())
    return [t for t in tokens if t not in COMMON_QUESTION_TOKENS]


def _list_csv_files():
    return sorted(glob.glob(os.path.join(CSV_DIR, "*.csv")))


def _read_header(path):
    try:
        df0 = pd.read_csv(path, nrows=0)
        return [c for c in df0.columns]
    except Exception:
        return []


def _read_sample(path, n=300):
    try:
        return pd.read_csv(path, nrows=n, low_memory=False)
    except Exception:
        return None


def _build_file_index():
    global FILE_INDEX
    if FILE_INDEX is not None:
        return FILE_INDEX

    index = []
    for path in _list_csv_files():
        name = os.path.basename(path).lower()
        name_tokens = set(re.findall(r"\w+", name))
        headers = _read_header(path)
        header_tokens = set()
        for header in headers:
            header_tokens |= set(re.findall(r"\w+", header.lower()))
        index.append({
            "path": path,
            "name": name,
            "name_tokens": name_tokens,
            "headers": headers,
            "header_tokens": header_tokens,
        })
    FILE_INDEX = index
    return FILE_INDEX


def _find_metric_token(question_tokens):
    for metric in METRIC_PRIORITY:
        if metric in question_tokens:
            return METRIC_SYNONYMS.get(metric, metric)
    for token in question_tokens:
        if token in METRIC_SYNONYMS:
            return METRIC_SYNONYMS[token]
    return None


def _score_file_for_question(file_meta, q_tokens, metric_token=None, raw_question=None):
    score = 0
    score += 1 * len(file_meta["name_tokens"] & set(q_tokens))
    score += 4 * len(file_meta["header_tokens"] & set(q_tokens))

    strong_metrics = {"cacat", "gini", "inflasi", "pengeluaran", "perkapita", "penduduk", "populasi"}
    if any(m in file_meta["name"] for m in strong_metrics):
        score += 6
    if any(m in file_meta["header_tokens"] for m in strong_metrics):
        score += 8

    if metric_token and metric_token in file_meta["name"]:
        score += 12
    if metric_token and metric_token in file_meta["header_tokens"]:
        score += 10

    raw_tokens = set(re.findall(r"\w+", raw_question.lower())) if raw_question else set(q_tokens)
    query_has_persentase = "persentase" in raw_tokens
    query_has_akta = any(tok in raw_tokens for tok in ["akta", "kelahiran"])
    query_has_usia = any(tok in raw_tokens for tok in ["usia", "sd", "sekolah"])
    query_has_sd = any(tok in raw_tokens for tok in ["sd", "sederajat"])
    query_has_disability = any(tok in raw_tokens for tok in ["disabilitas", "cacat", "penyandang"])
    query_has_miskin = any(tok in raw_tokens for tok in ["miskin", "termiskin"])
    query_has_terbanyak = any(tok in raw_tokens for tok in ["terbanyak", "tertinggi", "maksimal", "maksimum"])
    query_has_rata = any(tok in raw_tokens for tok in ["rata", "average", "mean"])
    query_has_kabupaten = any(tok in raw_tokens for tok in ["kabupaten", "kota"])

    if metric_token == "penduduk":
        file_has_persentase = "persentase" in file_meta["name_tokens"] or "persentase" in file_meta["header_tokens"]
        file_has_akta = any(tok in file_meta["name_tokens"] or tok in file_meta["header_tokens"] for tok in ["akta", "kelahiran"])
        file_has_disability = any(tok in file_meta["name"] or tok in file_meta["header_tokens"] for tok in ["disabilitas", "cacat", "penyandang"])
        file_has_usia_sekolah = "usia_sekolah" in file_meta["name"] or "usia_sekolah" in file_meta["header_tokens"]
        file_has_jenis_usia = "jenis_usia" in file_meta["name"] or "jenis_usia" in file_meta["header_tokens"]
        file_has_kategori_usia = "kategori_usia" in file_meta["name"] or "jenis_usia" in file_meta["name"] or "usia" in file_meta["name_tokens"] and "kategor" in file_meta["name"]

        if query_has_persentase:
            if file_has_persentase:
                score += 20
            if query_has_akta and file_has_akta:
                score += 30
            if query_has_akta and not file_has_akta and not file_has_persentase:
                score -= 16
            if file_has_persentase and not file_has_akta:
                score -= 6
        else:
            if file_has_persentase:
                score -= 18

        if "kepadatan" in file_meta["name_tokens"] or "kepadatan" in file_meta["header_tokens"]:
            score -= 14
        if "bpjs" in file_meta["name"] or "terdaftar" in file_meta["name"]:
            score -= 24
        if "keluhan" in file_meta["name"] or "keluhan" in file_meta["header_tokens"]:
            score -= 16

        if "jumlah_penduduk" in file_meta["name"] or "jumlah_penduduk" in file_meta["header_tokens"]:
            score += 22
        if "populasi" in file_meta["name"] or "populasi" in file_meta["header_tokens"]:
            score += 12
        if "provinsi_aceh" in file_meta["name"]:
            score += 8

        if query_has_usia:
            if file_has_usia_sekolah:
                score += 26
            if file_has_jenis_usia:
                score += 18
            if file_has_kategori_usia:
                score += 16
            if "sd" in file_meta["name_tokens"] or "sederajat" in file_meta["name_tokens"] or "sd" in file_meta["header_tokens"]:
                score += 18
            if "sekolah" in file_meta["name_tokens"] or "sekolah" in file_meta["header_tokens"]:
                score += 14
            if "usia" in file_meta["name_tokens"] or "usia" in file_meta["header_tokens"]:
                score += 12
            if file_has_disability and not query_has_disability:
                score -= 28

        if query_has_sd:
            if file_has_usia_sekolah:
                score += 30
            if "sd" in file_meta["name_tokens"] or "sederajat" in file_meta["name_tokens"]:
                score += 24

        if query_has_kabupaten and "kabupaten_kota" in file_meta["name"]:
            score += 24
        if query_has_kabupaten and ("kabupaten" in file_meta["name_tokens"] or "kota" in file_meta["name_tokens"]):
            score += 10

        subgroup_tokens = ["usia", "sekolah", "status", "perkawinan", "pekerjaan", "jenis", "kelamin", "agama", "disabilitas", "kecamatan", "desa", "keluarga", "kk", "asuhan", "pendidikan"]
        if any(tok in file_meta["name"] for tok in subgroup_tokens) and not raw_tokens.intersection(subgroup_tokens):
            score -= 18

        if query_has_miskin:
            if "miskin" in file_meta["name"] or "miskin" in file_meta["header_tokens"]:
                score += 24

        if query_has_terbanyak and not query_has_miskin:
            if "miskin" in file_meta["name"] or "miskin" in file_meta["header_tokens"]:
                score -= 20
            if "jumlah_penduduk" in file_meta["name"] or "jumlah_penduduk" in file_meta["header_tokens"]:
                score += 18
            if "populasi" in file_meta["name"] or "populasi" in file_meta["header_tokens"]:
                score += 10

        if query_has_rata:
            if "rata" in file_meta["name"] or "average" in file_meta["name"] or "mean" in file_meta["name"]:
                score += 20
            else:
                score -= 10

    # penalize overly generic filename matches
    if "jumlah" in file_meta["name_tokens"] or "nilai" in file_meta["name_tokens"]:
        score -= 1

    return score


def _best_candidate_paths(question, top_k=None):
    file_index = _build_file_index()
    q_tokens = _tokens(question)
    metric_token = _find_metric_token(q_tokens)
    scored = []
    for meta in file_index:
        score = _score_file_for_question(meta, q_tokens, metric_token, question)
        if score > 0:
            scored.append((score, meta["path"]))
    scored.sort(reverse=True)
    if not scored:
        return [meta["path"] for meta in file_index]
    if top_k is None:
        return [path for _, path in scored]
    return [path for _, path in scored[:top_k]]


def _find_column(cols, keywords):
    cols_l = [c.lower() for c in cols]
    for kw in keywords:
        for idx, c in enumerate(cols_l):
            if kw in c:
                return cols[idx]
    return None


MAX_PREFERENCE_KEYWORDS = [
    "terbanyak",
    "paling banyak",
    "terbesar",
    "maksimal",
    "maksimum",
    "tertinggi",
    "paling tinggi",
    "terutama",
    "paling banyak penduduk",
    "termiskin",
]

MIN_PREFERENCE_KEYWORDS = [
    "terkecil",
    "terendah",
    "paling sedikit",
    "minimum",
    "minimum",
    "terkecil",
    "terendah",
]


def _find_best_metric_column(cols, metric_token=None):
    cols_l = [c.lower() for c in cols]
    candidates = []
    if metric_token and metric_token in METRIC_COLUMN_PATTERNS:
        for pattern in METRIC_COLUMN_PATTERNS[metric_token]:
            for idx, cl in enumerate(cols_l):
                if pattern in cl:
                    candidates.append((100 + len(pattern), cols[idx]))
    elif metric_token is not None:
        # If we recognized a metric token but there's no strong matching column,
        # avoid returning a generic column for unrelated user queries.
        return None
    # Additional heuristic: prefer percentage-like columns for penduduk queries
    if metric_token == "penduduk":
        for idx, cl in enumerate(cols_l):
            if "persent" in cl or "persentase" in cl or "persentanse" in cl:
                candidates.append((120, cols[idx]))
    for idx, cl in enumerate(cols_l):
        score = 0
        if "cacat" in cl:
            score += 30
        if "penderita" in cl:
            score += 20
        if "gini" in cl or "rasio_gini" in cl or "gini_rasio" in cl:
            score += 30
        if "inflasi" in cl:
            score += 30
        if "pengeluaran" in cl or "belanja" in cl or "biaya" in cl:
            score += 20
        if "perkapita" in cl or "per_kapita" in cl:
            score += 20
        if "penduduk" in cl or "populasi" in cl:
            score += 15
        if "jumlah" in cl or "total" in cl or "count" in cl:
            score += 5
        if metric_token and metric_token in cl:
            score += 10
        if score > 0:
            candidates.append((score, cols[idx]))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]


def _find_query_category_filter(question, cols):
    text = str(question).lower()
    if any(tok in text for tok in ["sd", "sekolah", "usia"]):
        age_col = _find_column(cols, ["usia_sekolah", "jenis_usia", "kelompok_umur", "kelompok_usia", " jenjang", "jenjang", "usia"])  # noqa: E501
        if age_col is not None:
            return age_col
    return None


def _matches_category_value(value):
    if value is None:
        return False
    text = str(value).lower()
    return bool(re.search(r"\bsd\b|sekolah|sekolah dasar|dasar", text))


def _question_extreme_preference(question):
    text = _normalize_text(question)
    for keyword in MAX_PREFERENCE_KEYWORDS:
        if keyword in text:
            return "max"
    for keyword in MIN_PREFERENCE_KEYWORDS:
        if keyword in text:
            return "min"
    return None


def _normalize_region_text(value):
    if value is None:
        return ""
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def _row_matches_region(row, region_col, region):
    if region_col is None or region is None:
        return True
    try:
        cell = _normalize_region_text(row.get(region_col))
        return region.lower() in cell
    except Exception:
        return False


def _row_matches_year(row, year_col, year):
    if year_col is None or year is None:
        return True
    try:
        return str(row.get(year_col)).strip() == str(year)
    except Exception:
        return False


def _human_label(label):
    if not label:
        return "nilai"
    label = str(label).replace("_", " ").strip()
    return " ".join([word.capitalize() for word in label.split()])


def _format_answer(label, region_name, year_val, val):
    parts = [label]
    if region_name:
        parts.append(str(region_name))
    if year_val and str(year_val).lower() != "nan":
        parts.append(str(year_val))
    parts.append(str(val))
    return " ".join(parts)


def answer(question, region=None, year=None):
    q_tokens = _tokens(question)
    metric_token = _find_metric_token(q_tokens)
    if metric_token is None:
        return None, None
    candidates = _best_candidate_paths(question, top_k=None)
    if not candidates:
        candidates = _list_csv_files()

    raw_tokens = set(re.findall(r"\w+", question.lower()))
    query_has_persentase = any(tok.startswith("persent") for tok in raw_tokens)

    for path in candidates:
        df_sample = _read_sample(path, n=500)
        if df_sample is None or df_sample.empty:
            continue
        cols = list(df_sample.columns)
        region_col = _find_column(cols, REGION_COLUMN_PATTERNS)
        year_col = _find_column(cols, YEAR_COLUMN_PATTERNS)
        metric_col = _find_best_metric_column(cols, metric_token)
        if metric_col is None:
            metric_col = _find_column(cols, ["jumlah", "nilai", "total", "count"])

        if metric_col is None:
            continue

        # If user asked for percentages, prefer files whose `satuan`/unit column
        # indicates percent. If no percent unit exists in this file, skip it.
        if query_has_persentase:
            satuan_col = _find_column(cols, ["satuan", "unit"])
            if satuan_col is not None:
                try:
                    units = df_sample[satuan_col].astype(str).str.lower().unique()
                    has_percent = any((u and ("persen" in u or "persent" in u or "percent" in u)) for u in units)
                    if not has_percent:
                        continue
                except Exception:
                    pass

        sel = df_sample
        if region_col and region:
            sel = sel[sel[region_col].astype(str).str.lower().str.contains(str(region).lower(), na=False)]

        age_filter_col = _find_query_category_filter(question, cols)
        if age_filter_col is not None:
            age_mask = sel[age_filter_col].astype(str).apply(_matches_category_value)
            if not age_mask.any():
                continue
            sel = sel[age_mask]

        region_sel = sel.copy()
        if year_col and year:
            sel = sel[sel[year_col].astype(str).str.lower() == str(year).lower()]

        if sel.empty:
            if year_col and year and region_col and region and not region_sel.empty:
                try:
                    region_sel[year_col] = pd.to_numeric(region_sel[year_col], errors="coerce")
                    region_sel = region_sel.dropna(subset=[year_col])
                    if not region_sel.empty:
                        latest_idx = region_sel[year_col].idxmax()
                        chosen_row = region_sel.loc[latest_idx]
                        val = chosen_row.get(metric_col)
                        region_name = chosen_row.get(region_col)
                        actual_year = chosen_row.get(year_col)
                        answer_text = (
                            f"Data untuk tahun {year} di {region_name} tidak tersedia. "
                            f"Data terakhir yang tersedia adalah tahun {actual_year}: "
                            f"{_format_answer(_human_label(metric_col), region_name, actual_year, val)}"
                        )
                        dataset_url = _get_dataset_url_for_csv_path(path)
                        if dataset_url:
                            return answer_text, dataset_url
                        relative_path = os.path.relpath(path, ROOT)
                        return answer_text, relative_path
                except Exception:
                    pass
            continue

        try:
            vals = sel[metric_col].dropna()
        except Exception:
            try:
                vals = sel[metric_col].astype(str).replace("nan", "").replace("None", "").loc[lambda x: x.astype(bool)]
            except Exception:
                vals = []

        if len(vals) == 0:
            continue

        chosen_row = None
        if year_col and year_col in sel.columns and year:
            chosen_row = sel.loc[sel[sel[year_col].astype(str).str.strip() == str(year).strip()].index]
            if not chosen_row.empty:
                chosen_row = chosen_row.iloc[0]
            else:
                chosen_row = None
        if chosen_row is None:
            preference = _question_extreme_preference(question)
            if preference and metric_col in sel.columns:
                try:
                    numeric_values = pd.to_numeric(sel[metric_col], errors="coerce")
                    numeric_values = numeric_values.dropna()
                    if not numeric_values.empty:
                        if preference == "max":
                            chosen_row = sel.loc[numeric_values.idxmax()]
                        else:
                            chosen_row = sel.loc[numeric_values.idxmin()]
                except Exception:
                    chosen_row = None

            if chosen_row is None:
                try:
                    sel_year = pd.to_numeric(sel[year_col], errors="coerce") if year_col else None
                    if sel_year is not None and not sel_year.dropna().empty:
                        latest_idx = sel_year.dropna().idxmax()
                        chosen_row = sel.loc[latest_idx]
                    else:
                        chosen_row = sel.iloc[0]
                except Exception:
                    chosen_row = sel.iloc[0]

        val = chosen_row.get(metric_col)
        region_name = chosen_row.get(region_col) if region_col else region
        year_val = chosen_row.get(year_col) if year_col else year
        answer_text = _format_answer(_human_label(metric_col), region_name, year_val, val)
        dataset_url = _get_dataset_url_for_csv_path(path)
        if dataset_url:
            return answer_text, dataset_url

        relative_path = os.path.relpath(path, ROOT)
        return answer_text, relative_path

    return (None, None)
