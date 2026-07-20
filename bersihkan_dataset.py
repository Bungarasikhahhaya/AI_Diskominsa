"""
Pembersihan & Standardisasi Dataset — Modul 3 (Prediksi Tren)

Struktur folder yang diasumsikan:
    AI prediksi tren/
    ├── dataset_modul3_prediksi/       <- CSV mentah hasil scraping
    ├── dataset_bersih/                <- output tidy CSV (dibuat otomatis)
    ├── audit_kualitas_dataset.csv     <- hasil dari audit_kualitas_dataset.py
    ├── ekstrak_langsung_modul3.py
    ├── audit_kualitas_dataset.py
    └── bersihkan_dataset.py           <- taruh script ini di sini

Semua dataset dari satudata.acehprov.go.id ternyata pakai skema kolom yang
SAMA (standar Satu Data Indonesia / BPS):
    - Kolom identitas wilayah berjenjang: bps_kode_provinsi -> kabupaten_kota
      -> kecamatan -> desa (kosong/NaN kalau levelnya lebih tinggi)
    - tahun (selalu ada)
    - 0-2 kolom breakdown tambahan yang beda-beda per dataset
      (contoh: 'bulan', 'daerah', 'kelompok_umur')
    - 1 kolom nilai yang beda-beda per dataset (target prediksi)
    - Metadata: satuan, tingkat_penyajian, created_at, updated_at, deleted_at,
      id, uuid

Script ini otomatis mendeteksi level wilayah, kolom breakdown, dan kolom
nilai untuk SETIAP dataset "BAGUS" dari hasil audit, lalu menyimpan versi
tidy-nya (tahun, [breakdown], nilai, satuan, level_wilayah, nama_wilayah)
ke folder dataset_bersih/.

Cara pakai:
    pip install pandas
    python bersihkan_dataset.py
"""

import re
import pandas as pd
from pathlib import Path

FOLDER_MENTAH = "data/data/csv"
FOLDER_BERSIH = "dataset_bersih"
AUDIT_CSV = "audit_kualitas_dataset.csv"
PROGRESS_SETIAP = 200  # print progress tiap N file, karena volumenya besar

# Kolom-kolom standar Satu Data Indonesia yang BUKAN kolom nilai/breakdown
KOLOM_STANDAR = {
    "bps_kode_provinsi", "bps_nama_provinsi",
    "kemendagri_kode_provinsi", "kemendagri_nama_provinsi",
    "bps_kode_kabupaten_kota", "bps_nama_kabupaten_kota",
    "kemendagri_kode_kabupaten_kota", "kemendagri_nama_kabupaten_kota",
    "bps_kode_kecamatan", "bps_nama_kecamatan",
    "kemendagri_kode_kecamatan", "kemendagri_nama_kecamatan",
    "bps_kode_desa", "bps_nama_desa",
    "kemendagri_kode_desa", "kemendagri_nama_desa",
    "tahun", "tingkat_penyajian",
    "created_at", "updated_at", "deleted_at",
    "id", "uuid",
}


def parse_angka_indonesia(x):
    """
    Konversi string angka format Indonesia ke float.
    Contoh: "4,99" -> 4.99 | "1.234,56" -> 1234.56 | "1234.56" -> 1234.56 | 5 -> 5.0

    BPS/pemerintah sering pakai koma sebagai pemisah desimal (bukan titik
    seperti standar Python), jadi pd.to_numeric() biasa akan gagal/salah
    parse tanpa fungsi ini.
    """
    if pd.isna(x):
        return None
    s = str(x).strip()
    if s == "":
        return None
    # Kalau ada titik DAN koma: asumsikan titik = pemisah ribuan, koma = desimal
    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        # Cuma ada koma -> asumsikan itu pemisah desimal ala Indonesia
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def deteksi_level_wilayah(df):
    """Tentukan level wilayah paling detail yang terisi di dataset ini."""
    if "bps_kode_desa" in df.columns and df["bps_kode_desa"].notna().any():
        return "desa"
    if "bps_kode_kecamatan" in df.columns and df["bps_kode_kecamatan"].notna().any():
        return "kecamatan"
    if "bps_kode_kabupaten_kota" in df.columns and df["bps_kode_kabupaten_kota"].notna().any():
        return "kabupaten_kota"
    return "provinsi"


def kolom_nama_wilayah(level):
    """Kolom nama wilayah yang dipakai sesuai level."""
    mapping = {
        "provinsi": "bps_nama_provinsi",
        "kabupaten_kota": "bps_nama_kabupaten_kota",
        "kecamatan": "bps_nama_kecamatan",
        "desa": "bps_nama_desa",
    }
    return mapping[level]


def deteksi_kolom_breakdown_dan_nilai(df):
    """
    Dari kolom-kolom di luar KOLOM_STANDAR dan 'satuan':
    - kolom numerik -> kandidat kolom NILAI
    - kolom non-numerik -> kolom BREAKDOWN (misal 'bulan', 'daerah')
    """
    kandidat = [c for c in df.columns if c not in KOLOM_STANDAR and c != "satuan"]

    kolom_nilai = []
    kolom_breakdown = []
    for c in kandidat:
        if pd.api.types.is_numeric_dtype(df[c]):
            kolom_nilai.append(c)
        else:
            # Coba parse pakai parser format Indonesia (koma desimal),
            # bukan pd.to_numeric biasa yang gagal pada "4,99"
            converted = df[c].apply(parse_angka_indonesia)
            if converted.notna().sum() >= len(df) * 0.5:  # mayoritas berhasil dikonversi
                kolom_nilai.append(c)
            else:
                kolom_breakdown.append(c)

    return kolom_breakdown, kolom_nilai


def baca_csv_aman(path):
    """Baca CSV dengan fallback encoding, karena dataset sebanyak ini
    kemungkinan ada variasi encoding (UTF-8 biasa vs UTF-8 dengan BOM)."""
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="utf-8-sig")


def bersihkan_satu_dataset(path_csv):
    """Return tidy DataFrame dari 1 file CSV mentah, atau None kalau gagal."""
    df = baca_csv_aman(path_csv)

    if "tahun" not in df.columns:
        return None, "tidak ada kolom 'tahun'"

    level = deteksi_level_wilayah(df)
    kolom_wilayah = kolom_nama_wilayah(level)
    kolom_breakdown, kolom_nilai = deteksi_kolom_breakdown_dan_nilai(df)

    if not kolom_nilai:
        return None, "tidak ditemukan kolom nilai numerik"

    # Kalau ada lebih dari 1 kandidat kolom nilai, ambil yang paling "penuh" (sedikit NaN)
    if len(kolom_nilai) > 1:
        kolom_nilai_terpilih = df[kolom_nilai].notna().sum().idxmax()
    else:
        kolom_nilai_terpilih = kolom_nilai[0]

    kolom_dipakai = ["tahun"] + kolom_breakdown + [kolom_nilai_terpilih]
    if kolom_wilayah in df.columns:
        kolom_dipakai = [kolom_wilayah] + kolom_dipakai

    tidy = df[kolom_dipakai].copy()
    tidy = tidy.rename(columns={
        kolom_nilai_terpilih: "nilai",
        kolom_wilayah: "wilayah",
    })
    tidy["nilai"] = tidy["nilai"].apply(parse_angka_indonesia)
    tidy["level_wilayah"] = level
    if "satuan" in df.columns:
        tidy["satuan"] = df["satuan"]

    tidy = tidy.dropna(subset=["nilai"])
    tidy = tidy.sort_values("tahun")

    return tidy, None


def main():
    audit = pd.read_csv(AUDIT_CSV)
    bagus = audit[audit["status"] == "BAGUS (siap prediksi)"]
    print(f"Dataset berstatus BAGUS: {len(bagus)}")

    out_dir = Path(FOLDER_BERSIH)
    out_dir.mkdir(exist_ok=True)

    ringkasan = []
    total = len(bagus)
    for idx, (_, row) in enumerate(bagus.iterrows(), start=1):
        if idx % PROGRESS_SETIAP == 0 or idx == total:
            print(f"  ... progress: {idx}/{total}")

        nama_file = row["file"]
        path_csv = Path(FOLDER_MENTAH) / nama_file

        if not path_csv.exists():
            ringkasan.append({"file": nama_file, "status": "FILE TIDAK DITEMUKAN"})
            continue

        try:
            tidy, error = bersihkan_satu_dataset(path_csv)
        except Exception as e:
            ringkasan.append({"file": nama_file, "status": f"ERROR: {e}"})
            continue

        if tidy is None:
            ringkasan.append({"file": nama_file, "status": f"DILEWATI ({error})"})
            continue

        out_path = out_dir / nama_file
        tidy.to_csv(out_path, index=False)
        ringkasan.append({
            "file": nama_file,
            "status": "OK",
            "baris_bersih": len(tidy),
            "level_wilayah": tidy["level_wilayah"].iloc[0] if len(tidy) else "-",
            "kolom_breakdown": [c for c in tidy.columns if c not in
                                 ("tahun", "nilai", "wilayah", "level_wilayah", "satuan")],
        })

    df_ringkasan = pd.DataFrame(ringkasan)
    df_ringkasan.to_csv("ringkasan_pembersihan.csv", index=False)

    print("\n" + "=" * 60)
    ok = (df_ringkasan["status"] == "OK").sum()
    print(f"Berhasil dibersihkan: {ok} / {len(df_ringkasan)}")
    print(f"Detail tersimpan di: ringkasan_pembersihan.csv")
    print(f"File tidy tersimpan di folder: {FOLDER_BERSIH}/")
    print("=" * 60)

    gagal = df_ringkasan[df_ringkasan["status"] != "OK"]
    if not gagal.empty:
        print("\nFile yang dilewati/gagal:")
        print(gagal[["file", "status"]].to_string(index=False))


if __name__ == "__main__":
    main()
