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
    "miskin",
    "penduduk",
    "populasi",
]

METRIC_SYNONYMS = {
    "disabilitas": "cacat",
    "penyandang": "cacat",
    "kemiskinan": "miskin",
    "miskin": "miskin",
}

METRIC_COLUMN_PATTERNS = {
    "cacat": ["jumlah_penderita_cacat", "jumlah_cacat", "penderita_cacat", "cacat"],
    "disabilitas": ["disabilitas"],
    "penderita": ["jumlah_penderita", "penderita"],
    "gini": ["gini", "rasio_gini", "gini_rasio"],
    "inflasi": ["inflasi"],
    "pengeluaran": ["pengeluaran", "belanja", "biaya"],
    "perkapita": ["perkapita", "per_kapita"],
    "miskin": ["jumlah_penduduk_miskin", "penduduk_miskin", "jumlah_penduduk_miskin_ekstrem", "persentase_penduduk_miskin", "miskin", "kemiskinan"],
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
MONTH_COLUMN_PATTERNS = ["bulan", "month"]

MONTH_ALIASES = {
    "januari": "januari", "februari": "februari", "maret": "maret",
    "april": "april", "mei": "mei", "juni": "juni", "juli": "juli",
    "agustus": "agustus", "september": "september", "oktober": "oktober",
    "november": "november", "desember": "desember",
}

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
        # Once a metric is recognized, only a column explicitly associated
        # with that metric is valid.  A generic numeric-looking column from a
        # different dataset (for example, `proporsi_penduduk...` for an
        # inflation question) must never be selected.
        if not candidates:
            return None
        candidates.sort(reverse=True)
        return candidates[0][1]
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


def _extract_named_category(question):
    """Extract a category requested as 'kelompok X', 'kategori X', etc."""
    match = re.search(
        r"\b(kelompok|kategori|subsektor|jenis)\s+(.+?)(?:[?!.]|$)",
        str(question).lower(),
    )
    if not match:
        return None, None
    label = _normalize_text(match.group(2))
    return match.group(1), label or None


def _find_named_category_column(cols, category_kind):
    if category_kind is None:
        return None
    alternatives = {
        "kelompok": ["kelompok", "kategori"],
        "kategori": ["kategori", "kelompok"],
        "subsektor": ["subsektor"],
        "jenis": ["jenis"],
    }
    patterns = alternatives.get(category_kind, [category_kind])

    # Prefer an exact label column (e.g. `kelompok`) over an identifier such
    # as `kode_kelompok`; the user's phrase is a label, not a numeric code.
    for pattern in patterns:
        for col in cols:
            if str(col).lower().strip() == pattern:
                return col

    return _find_column(cols, patterns)


def _filter_by_named_category(df, category_col, category_value):
    if category_col is None or category_value is None:
        return df
    return df[df[category_col].apply(
        lambda value: _normalize_text(value) == category_value
    )]


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


def _extract_year_ints(value):
    """Return list of 4-digit year ints (1900-2099) found in the value."""
    try:
        s = str(value)
        years = re.findall(r"\b(?:19|20)\d{2}\b", s)
        return [int(y) for y in years]
    except Exception:
        return []


def _matches_year_value(value, year):
    """Flexible matching of a dataset year cell against the requested year.

    Handles exact string matches, numeric appearances inside ranges (e.g. "2018-2019"),
    comma/semicolon separated lists, and simple token matches.
    """
    if value is None:
        return False
    try:
        y = str(year).strip()
        if y == "":
            return False
        s = str(value)
        # Exact normalized match
        if s.strip().lower() == y.lower():
            return True
        # If the cell contains numeric year tokens, check those
        ints = _extract_year_ints(s)
        try:
            yi = int(y)
        except Exception:
            yi = None
        if yi is not None and ints:
            if yi in ints:
                return True
        # token boundary match (handles e.g. '2018/2019' if y is '2018')
        if re.search(r"\b" + re.escape(y) + r"\b", s):
            return True
        # split common separators and compare tokens
        parts = re.split(r"[;,/|\\s]+", s)
        if any(p.strip().lower() == y.lower() for p in parts):
            return True
        return False
    except Exception:
        return False


def _row_matches_year(row, year_col, year):
    if year_col is None or year is None:
        return True
    try:
        return _matches_year_value(row.get(year_col), year)
    except Exception:
        return False


def _matches_month_value(value, month):
    if value is None or month is None:
        return False
    actual = _normalize_text(value)
    requested = MONTH_ALIASES.get(_normalize_text(month), _normalize_text(month))
    return actual == requested


def _filter_by_period(df, year_col, year, month_col, month):
    """Filter a dataframe by every requested time component."""
    result = df
    if year_col and year:
        result = result[result[year_col].apply(lambda v: _matches_year_value(v, year))]
    if month_col and month:
        result = result[result[month_col].apply(lambda v: _matches_month_value(v, month))]
    return result


def _select_best_row(df, year_col, metric_col, question=None, year=None):
    if df is None or df.empty or metric_col not in df.columns:
        return None

    if year_col and year is not None:
        try:
            matched = df.loc[df[year_col].astype(str).apply(lambda v: _matches_year_value(v, year))]
            if not matched.empty:
                return matched.iloc[0]
        except Exception:
            try:
                matched = df.loc[df[year_col].astype(str).str.strip() == str(year).strip()]
                if not matched.empty:
                    return matched.iloc[0]
            except Exception:
                pass

    preference = _question_extreme_preference(question or "")
    if preference:
        try:
            numeric_values = pd.to_numeric(df[metric_col], errors="coerce").dropna()
            if not numeric_values.empty:
                if preference == "max":
                    return df.loc[numeric_values.idxmax()]
                return df.loc[numeric_values.idxmin()]
        except Exception:
            pass

    if year_col in df.columns:
        try:
            df_year = df.copy()
            df_year["__year_max"] = df_year[year_col].astype(str).apply(lambda v: max(_extract_year_ints(v)) if _extract_year_ints(v) else None)
            df_year = df_year.dropna(subset=["__year_max"])
            if not df_year.empty:
                return df_year.loc[df_year["__year_max"].idxmax()]
        except Exception:
            pass

    try:
        return df.iloc[0]
    except Exception:
        return None


def _human_label(label):
    if not label:
        return "nilai"
    label = str(label).replace("_", " ").strip()
    return " ".join([word.capitalize() for word in label.split()])


def _is_missing_value(value):
    if value is None:
        return True
    text = str(value).strip().lower()
    return text == "" or text == "nan" or text == "none"


def _format_answer(label, region_name, year_val, val):
    parts = [label]
    if not _is_missing_value(region_name):
        parts.append(str(region_name))
    if not _is_missing_value(year_val):
        parts.append(str(year_val))
    parts.append(str(val))
    return " ".join(parts)


def _format_trend_answer(label, region_name, year_val, val):
    label_text = label.lower()
    region_text = f" di {region_name}" if not _is_missing_value(region_name) else ""
    year_text = f" pada tahun {year_val}" if not _is_missing_value(year_val) else ""
    return f"Tren {label_text}{year_text}{region_text} adalah {val}."


def answer(question, region=None, year=None, month=None, trend=False):
    q_tokens = _tokens(question)
    metric_token = _find_metric_token(q_tokens)
    if metric_token is None:
        return None, None
    candidates = _best_candidate_paths(question, top_k=None)
    if not candidates:
        candidates = _list_csv_files()

    raw_tokens = set(re.findall(r"\w+", question.lower()))
    query_has_persentase = any(tok.startswith("persent") for tok in raw_tokens)
    category_kind, category_value = _extract_named_category(question)

    for path in candidates:
        df_sample = _read_sample(path, n=500)
        if df_sample is None or df_sample.empty:
            continue
        cols = list(df_sample.columns)
        region_col = _find_column(cols, REGION_COLUMN_PATTERNS)
        year_col = _find_column(cols, YEAR_COLUMN_PATTERNS)
        month_col = _find_column(cols, MONTH_COLUMN_PATTERNS)
        category_col = _find_named_category_column(cols, category_kind)
        metric_col = _find_best_metric_column(cols, metric_token)

        # A category named by the user is a mandatory constraint.  A dataset
        # without a compatible category column cannot answer that question,
        # even if it contains a similarly named metric such as inflation.
        if category_value is not None and category_col is None:
            continue

        # A recognized metric (for example, "inflasi") must be backed by a
        # matching column.  Do not fall back to generic numeric fields such as
        # `id`, `jumlah`, or `nilai` from an unrelated dataset.
        if metric_col is None and metric_token is None:
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

        # The sample is used only to inspect the schema.  Apply the user's
        # filters to the complete CSV so matches after the first 500 rows are
        # not silently missed.
        try:
            sel = pd.read_csv(path, low_memory=False)
        except Exception:
            continue
        if region_col and region:
            sel = sel[sel[region_col].astype(str).str.lower().str.contains(str(region).lower(), na=False)]

        sel = _filter_by_named_category(sel, category_col, category_value)

        age_filter_col = _find_query_category_filter(question, cols)
        if age_filter_col is not None:
            age_mask = sel[age_filter_col].astype(str).apply(_matches_category_value)
            if not age_mask.any():
                continue
            sel = sel[age_mask]

        sel = _filter_by_period(sel, year_col, year, month_col, month)

        if sel.empty:
            # Never substitute a different period for a period explicitly
            # requested by the user.  That produces plausible but false facts.
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

        # Prefer verifying the requested region/year against the full CSV to avoid
        # returning a candidate dataset that does not actually contain the row.
        chosen_row = None
        if os.path.exists(path) and (region or year):
            try:
                df_full = pd.read_csv(path, low_memory=False)
                if region_col and region:
                    df_full = df_full[df_full[region_col].astype(str).str.lower().str.contains(str(region).lower(), na=False)]
                df_full = _filter_by_named_category(df_full, category_col, category_value)
                df_full = _filter_by_period(df_full, year_col, year, month_col, month)
                if df_full.empty:
                    continue
                chosen_row = _select_best_row(df_full, year_col, metric_col, question=question, year=year)
            except Exception:
                chosen_row = None

        if chosen_row is None:
            if year_col and year_col in sel.columns and year:
                try:
                    chosen_row = sel.loc[sel[sel[year_col].astype(str).apply(lambda v: _matches_year_value(v, year))].index]
                    if not chosen_row.empty:
                        chosen_row = chosen_row.iloc[0]
                    else:
                        chosen_row = None
                except Exception:
                    chosen_row = sel.loc[sel[sel[year_col].astype(str).str.strip() == str(year).strip()].index]
                    if not chosen_row.empty:
                        chosen_row = chosen_row.iloc[0]
                    else:
                        chosen_row = None
            # chosen_row already normalized inside try/except above
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
                    if year_col:
                        # compute best numeric hint per-row and pick latest
                        sel = sel.copy()
                        sel["__year_max"] = sel[year_col].astype(str).apply(lambda v: max(_extract_year_ints(v)) if _extract_year_ints(v) else None)
                        if not sel["__year_max"].dropna().empty:
                            latest_idx = sel["__year_max"].idxmax()
                            chosen_row = sel.loc[latest_idx]
                        else:
                            chosen_row = sel.iloc[0]
                    else:
                        chosen_row = sel.iloc[0]
                except Exception:
                    chosen_row = sel.iloc[0]

        if chosen_row is None:
            continue

        val = chosen_row.get(metric_col)
        region_name = chosen_row.get(region_col) if region_col else region
        year_val = chosen_row.get(year_col) if year_col else year
        if trend and year_val:
            label = _human_label(metric_col)
            if metric_token and metric_token != label.lower():
                label = label
            answer_text = (
                f"Tren {label.lower()} pada tahun {year_val} "
                f"di {region_name or 'Aceh'} adalah {val}."
            )
        else:
            answer_text = _format_answer(_human_label(metric_col), region_name, year_val, val)
        dataset_url = _get_dataset_url_for_csv_path(path)
        # If a catalog URL exists for this dataset, prefer returning a local
        # relative file path when the local CSV contains data for the
        # requested year (and thus is more authoritative for year-specific
        # queries). Otherwise return the catalog URL.
        try:
            if dataset_url and os.path.exists(path) and year is not None:
                try:
                    df_full = pd.read_csv(path, low_memory=False)
                    cols_full = list(df_full.columns)
                    year_col_full = _find_column(cols_full, YEAR_COLUMN_PATTERNS)
                    metric_col_full = metric_col or _find_best_metric_column(cols_full, metric_token)
                    region_col_full = region_col
                    if year_col_full is not None:
                        month_col_full = _find_column(cols_full, MONTH_COLUMN_PATTERNS)
                        category_col_full = _find_named_category_column(cols_full, category_kind)
                        df_y = _filter_by_period(df_full, year_col_full, year, month_col_full, month)
                        df_y = _filter_by_named_category(df_y, category_col_full, category_value)
                        if region_col_full is not None and region is not None:
                            df_y = df_y[df_y[region_col_full].astype(str).str.lower().str.contains(str(region).lower(), na=False)]
                        if not df_y.empty and metric_col_full is not None:
                            df_y = df_y.copy()
                            df_y['_mnum'] = pd.to_numeric(df_y[metric_col_full], errors='coerce')
                            if not df_y['_mnum'].dropna().empty:
                                chosen_row_local = _select_best_row(
                                    df_y, year_col_full, metric_col_full,
                                    question=question, year=year,
                                )
                                val_local = chosen_row_local.get(metric_col_full)
                                region_name_local = chosen_row_local.get(region_col_full) if region_col_full else region
                                year_val_local = chosen_row_local.get(year_col_full)
                                if trend and year_val_local:
                                    answer_text_local = _format_trend_answer(
                                        _human_label(metric_col_full),
                                        region_name_local,
                                        year_val_local,
                                        val_local,
                                    )
                                else:
                                    answer_text_local = _format_answer(
                                        _human_label(metric_col_full),
                                        region_name_local,
                                        year_val_local,
                                        val_local,
                                    )
                                relative_path = os.path.relpath(path, ROOT)
                                return answer_text_local, (dataset_url if dataset_url else relative_path)
                except Exception:
                    pass
        except Exception:
            pass

        # If no year requested but we have a local file and a requested region,
        # prefer the local file's row for that region (choose latest year if multiple).
        try:
            if dataset_url and os.path.exists(path) and region is not None:
                try:
                    df_full = pd.read_csv(path, low_memory=False)
                    cols_full = list(df_full.columns)
                    region_col_full = _find_column(cols_full, REGION_COLUMN_PATTERNS)
                    metric_col_full = metric_col or _find_best_metric_column(cols_full, metric_token)
                    year_col_full = _find_column(cols_full, YEAR_COLUMN_PATTERNS)
                    category_col_full = _find_named_category_column(cols_full, category_kind)
                    if region_col_full is not None:
                        selr = df_full[df_full[region_col_full].astype(str).str.lower().str.contains(str(region).lower(), na=False)]
                        selr = _filter_by_named_category(selr, category_col_full, category_value)
                        if not selr.empty and metric_col_full is not None:
                            if year_col_full is not None:
                                selr = selr.copy()
                                selr["__year_max"] = selr[year_col_full].astype(str).apply(lambda v: max(_extract_year_ints(v)) if _extract_year_ints(v) else None)
                                selr = selr.dropna(subset=["__year_max"])
                                if not selr.empty:
                                    latest_idx = selr["__year_max"].idxmax()
                                    chosen_row_local = selr.loc[latest_idx]
                                else:
                                    chosen_row_local = selr.iloc[0]
                            else:
                                chosen_row_local = selr.iloc[0]

                            val_local = chosen_row_local.get(metric_col_full)
                            region_name_local = chosen_row_local.get(region_col_full)
                            year_val_local = chosen_row_local.get(year_col_full) if year_col_full else None
                            if trend and year_val_local:
                                answer_text_local = _format_trend_answer(
                                    _human_label(metric_col_full),
                                    region_name_local,
                                    year_val_local,
                                    val_local,
                                )
                            else:
                                answer_text_local = _format_answer(
                                    _human_label(metric_col_full),
                                    region_name_local,
                                    year_val_local,
                                    val_local,
                                )
                            relative_path = os.path.relpath(path, ROOT)
                            return answer_text_local, (dataset_url if dataset_url else relative_path)
                except Exception:
                    pass
        except Exception:
            pass

        if dataset_url:
            return answer_text, dataset_url

        relative_path = os.path.relpath(path, ROOT)
        return answer_text, relative_path

    return (None, None)
