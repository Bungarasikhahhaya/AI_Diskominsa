"""
Audit Kualitas Dataset — Modul 3 (Prediksi Tren)

Struktur folder yang diasumsikan:
    AI Prediksi Tren/
    ├── data/data/csv/             <- seluruh 3546 CSV hasil scraping tim
    ├── ekstrak_langsung_modul3.py
    └── audit_kualitas_dataset.py  <- taruh script ini di sini

Cek seluruh file CSV hasil scraping untuk menentukan mana yang beneran cocok
untuk analisis tren & proyeksi (punya data multi-tahun) vs yang tidak
relevan (snapshot satu waktu, tanpa dimensi tahun).

Kenapa ini penting sebelum bangun model:
Judul dataset yang mengandung kata "inflasi"/"kemiskinan"/dll belum tentu
isinya time-series. Bisa jadi cuma data 1 periode terbaru, atau breakdown
per kabupaten tanpa histori tahun. Model proyeksi butuh minimal ~3-4 titik
tahun berbeda per indikator/wilayah supaya masuk akal.

Cara pakai:
    pip install pandas
    python audit_kualitas_dataset.py
"""

import pandas as pd
import re
from pathlib import Path

FOLDER = "data/data/csv"  # relatif terhadap lokasi script ini
OUTPUT_CSV = "audit_kualitas_dataset.csv"
PROGRESS_SETIAP = 200  # print progress tiap N file, karena volumenya besar

YEAR_COL_PATTERNS = re.compile(r'(tahun|year|periode)', re.IGNORECASE)
YEAR_VALUE_PATTERN = re.compile(r'^(19|20)\d{2}$')  # kolom bernama angka tahun, misal "2021"


def detect_year_info(df):
    """
    Deteksi dimensi tahun dalam dataframe.

    Ada 2 kemungkinan format data:
    - long format : ada 1 kolom bernama semacam 'tahun'/'year'/'periode',
                     tiap baris = 1 tahun
    - wide format  : setiap tahun jadi nama kolom sendiri
                     ("2019", "2020", "2021", ...)

    Return: (mode, jumlah_tahun_unik, daftar_tahun)
    mode salah satu dari: 'long', 'wide', 'none'
    """
    # Cek long format
    long_col = None
    for col in df.columns:
        if YEAR_COL_PATTERNS.search(str(col)):
            long_col = col
            break
    if long_col is not None:
        tahun_unik = pd.to_numeric(df[long_col], errors='coerce').dropna().unique()
        tahun_unik = sorted([int(t) for t in tahun_unik if 1990 <= t <= 2100])
        if tahun_unik:
            return 'long', len(tahun_unik), tahun_unik

    # Cek wide format
    wide_years = [str(c) for c in df.columns if YEAR_VALUE_PATTERN.match(str(c).strip())]
    if wide_years:
        tahun_unik = sorted(int(y) for y in wide_years)
        return 'wide', len(tahun_unik), tahun_unik

    return 'none', 0, []


def klasifikasi_status(n_tahun):
    if n_tahun >= 3:
        return "BAGUS (siap prediksi)"
    elif n_tahun == 2:
        return "MARGINAL (cuma 2 titik tahun)"
    elif n_tahun == 1:
        return "SNAPSHOT (1 tahun saja)"
    else:
        return "TIDAK ADA DIMENSI TAHUN"


def baca_csv_aman(path):
    """Baca CSV dengan fallback encoding, karena dataset sebanyak ini
    kemungkinan ada variasi encoding (UTF-8 biasa vs UTF-8 dengan BOM)."""
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="utf-8-sig")


def audit_folder(folder_path):
    csv_files = list(Path(folder_path).glob("*.csv"))
    print(f"Total file CSV ditemukan: {len(csv_files)}")

    hasil_audit = []
    for i, f in enumerate(csv_files, start=1):
        if i % PROGRESS_SETIAP == 0 or i == len(csv_files):
            print(f"  ... progress: {i}/{len(csv_files)}")

        try:
            df = baca_csv_aman(f)
        except Exception as e:
            hasil_audit.append({
                "file": f.name, "status": "ERROR_BACA", "jumlah_baris": 0,
                "jumlah_kolom": 0, "mode_tahun": "-", "jumlah_tahun_unik": 0,
                "rentang_tahun": "-", "kolom": f"error: {e}"
            })
            continue

        mode, n_tahun, daftar_tahun = detect_year_info(df)
        status = klasifikasi_status(n_tahun)
        rentang = f"{min(daftar_tahun)}-{max(daftar_tahun)}" if daftar_tahun else "-"

        hasil_audit.append({
            "file": f.name,
            "status": status,
            "jumlah_baris": len(df),
            "jumlah_kolom": len(df.columns),
            "mode_tahun": mode,
            "jumlah_tahun_unik": n_tahun,
            "rentang_tahun": rentang,
            "kolom": ", ".join(str(c) for c in df.columns[:8]),  # 8 kolom pertama biar ringkas
        })

    return pd.DataFrame(hasil_audit)


def main():
    df_audit = audit_folder(FOLDER)

    if df_audit.empty:
        print(f"Tidak ada file CSV ditemukan di folder '{FOLDER}'. Cek kembali path-nya.")
        return

    print("\n" + "=" * 60)
    print("RINGKASAN STATUS")
    print("=" * 60)
    print(df_audit['status'].value_counts().to_string())

    error_baca = (df_audit['status'] == 'ERROR_BACA').sum()
    if error_baca:
        print(f"\n[!] {error_baca} file gagal dibaca sama sekali (cek kolom 'kolom' "
              f"di CSV output untuk detail errornya)")

    siap_pakai = (df_audit['jumlah_tahun_unik'] >= 3).sum()
    print(f"\nDataset SIAP untuk proyeksi tren (>=3 titik tahun): "
          f"{siap_pakai} dari {len(df_audit)}")

    # Simpan hasil audit lengkap
    df_audit_sorted = df_audit.sort_values('jumlah_tahun_unik', ascending=False)
    df_audit_sorted.to_csv(OUTPUT_CSV, index=False)
    print(f"\nHasil audit lengkap tersimpan ke: {OUTPUT_CSV}")

    # Tampilkan daftar dataset paling siap pakai (top 20 saja karena kemungkinan ratusan)
    print("\n" + "=" * 60)
    print("CONTOH 20 DATASET PALING SIAP (>=3 titik tahun, diurutkan terbanyak)")
    print("=" * 60)
    kandidat = df_audit_sorted[df_audit_sorted['jumlah_tahun_unik'] >= 3]
    if kandidat.empty:
        print("Tidak ada dataset dengan >=3 titik tahun. Cek dataset MARGINAL/SNAPSHOT "
              "secara manual, mungkin kolom tahunnya bernama tidak standar.")
    else:
        cols_to_show = ['file', 'jumlah_tahun_unik', 'rentang_tahun', 'jumlah_baris']
        print(kandidat[cols_to_show].head(20).to_string(index=False))
        print(f"\n(lihat semua {len(kandidat)} di {OUTPUT_CSV})")


if __name__ == "__main__":
    main()

