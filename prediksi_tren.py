"""
Prediksi & Proyeksi Tren — Modul 3

Struktur folder yang diasumsikan:
    AI Prediksi Tren/
    ├── dataset_bersih/          <- hasil dari bersihkan_dataset.py
    ├── hasil_proyeksi/          <- output (dibuat otomatis)
    ├── ...
    └── prediksi_tren.py         <- taruh script ini di sini

Untuk SETIAP dataset tidy di dataset_bersih/, script ini:
1. Kelompokkan berdasarkan wilayah + kolom breakdown (kalau ada, misal 'bulan'/'daerah')
2. Agregasi ke level TAHUNAN (rata-rata, kalau datanya bulanan)
3. Fit regresi linear sederhana (tahun -> nilai) sebagai baseline tren
4. Proyeksikan nilai 1-3 tahun ke depan
5. Hitung R^2 sebagai indikator seberapa "rapi" tren-nya (linear vs fluktuatif)

Catatan penting soal regresi linear sebagai baseline:
- Ini BUKAN model paling canggih, tapi paling gampang dijelaskan ke dosen/
  pembimbing dan robust untuk data tahunan yang titiknya sedikit (~5-25 titik).
- R^2 rendah (<0.3) artinya tren historisnya tidak benar-benar linear/naik-turun
  fluktuatif -> proyeksi linear kurang bisa diandalkan untuk kasus itu, script
  akan menandainya di kolom 'catatan'.
- Kalau nanti mau upgrade, tinggal ganti fungsi fit_dan_proyeksi() dengan
  model lain (Prophet dkk) tanpa ubah struktur pipeline lainnya.

Cara pakai:
    pip install pandas numpy
    python prediksi_tren.py
"""

import numpy as np
import pandas as pd
from pathlib import Path

FOLDER_BERSIH = "dataset_bersih"
FOLDER_OUTPUT = "hasil_proyeksi"
TAHUN_KE_DEPAN = 3  # proyeksi berapa tahun ke depan
MIN_TITIK_DATA = 3  # minimal titik tahun untuk bisa dibuat model

# Kolom yang merepresentasikan sub-granularitas waktu (bukan dimensi wilayah/
# kategori) -> harus DIAGREGASI ke tahunan, bukan dijadikan grup terpisah
KOLOM_WAKTU_SUB_TAHUNAN = {"bulan", "triwulan", "semester", "quarter", "kuartal"}


def agregasi_tahunan(df, kolom_grup):
    """
    Kelompokkan berdasarkan kolom_grup + tahun, ambil rata-rata nilai.
    Ini menangani kasus data bulanan (banyak baris per tahun) supaya jadi
    1 nilai per tahun sebelum masuk ke regresi.
    """
    return df.groupby(kolom_grup + ["tahun"], as_index=False)["nilai"].mean()


def fit_dan_proyeksi(tahun, nilai, tahun_ke_depan=TAHUN_KE_DEPAN):
    """
    Fit regresi linear sederhana (numpy polyfit derajat 1) dan proyeksikan
    N tahun ke depan dari titik data terakhir.

    Return dict berisi slope, r_squared, proyeksi per tahun, dan arah tren.
    """
    tahun = np.array(tahun, dtype=float)
    nilai = np.array(nilai, dtype=float)

    slope, intercept = np.polyfit(tahun, nilai, 1)
    prediksi_historis = slope * tahun + intercept

    # R^2
    ss_res = np.sum((nilai - prediksi_historis) ** 2)
    ss_tot = np.sum((nilai - np.mean(nilai)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    tahun_terakhir = int(tahun.max())
    proyeksi = {}
    for i in range(1, tahun_ke_depan + 1):
        tahun_target = tahun_terakhir + i
        proyeksi[tahun_target] = round(slope * tahun_target + intercept, 3)

    if abs(slope) < 1e-9:
        arah = "stabil"
    elif slope > 0:
        arah = "naik"
    else:
        arah = "turun"

    return {
        "slope_per_tahun": round(slope, 4),
        "r_squared": round(r_squared, 3),
        "arah_tren": arah,
        "tahun_terakhir": tahun_terakhir,
        "nilai_terakhir": round(nilai[-1], 3),
        "proyeksi": proyeksi,
    }


def proses_satu_file(path_csv):
    """Proses 1 file tidy CSV, return list of dict (1 dict per grup wilayah/breakdown)."""
    df = pd.read_csv(path_csv)

    if "tahun" not in df.columns or "nilai" not in df.columns:
        return [], "kolom 'tahun'/'nilai' tidak ada"

    kolom_grup = [
        c for c in df.columns
        if c not in ("tahun", "nilai", "satuan", "level_wilayah")
        and c.lower() not in KOLOM_WAKTU_SUB_TAHUNAN
    ]
    # level_wilayah & satuan cuma metadata, tidak dipakai sbg dimensi grouping,
    # tapi tetap kita simpan nilainya untuk pelaporan
    satuan = df["satuan"].iloc[0] if "satuan" in df.columns and len(df) else "-"
    level_wilayah = df["level_wilayah"].iloc[0] if "level_wilayah" in df.columns and len(df) else "-"

    df_tahunan = agregasi_tahunan(df, kolom_grup)

    hasil = []
    for kunci_grup, grup in df_tahunan.groupby(kolom_grup) if kolom_grup else [((), df_tahunan)]:
        grup = grup.sort_values("tahun")
        if len(grup) < MIN_TITIK_DATA:
            continue

        fit = fit_dan_proyeksi(grup["tahun"].tolist(), grup["nilai"].tolist())

        catatan = ""
        if fit["r_squared"] < 0.3:
            catatan = "Tren historis fluktuatif (R^2 rendah) - proyeksi linear kurang bisa diandalkan"
        elif fit["r_squared"] < 0.6:
            catatan = "Tren historis cukup fluktuatif - proyeksi linear sebagai estimasi kasar"

        baris = {
            "file_sumber": path_csv.name,
            "indikator": path_csv.stem,
            "level_wilayah": level_wilayah,
            "satuan": satuan,
            "jumlah_titik_tahun": len(grup),
            "tahun_terakhir": fit["tahun_terakhir"],
            "nilai_terakhir": fit["nilai_terakhir"],
            "slope_per_tahun": fit["slope_per_tahun"],
            "r_squared": fit["r_squared"],
            "arah_tren": fit["arah_tren"],
            "catatan": catatan,
        }
        # kolom grup (wilayah, breakdown lain) dimasukkan sebagai kolom terpisah
        if kolom_grup:
            if not isinstance(kunci_grup, tuple):
                kunci_grup = (kunci_grup,)
            for nama_kolom, nilai_kolom in zip(kolom_grup, kunci_grup):
                baris[nama_kolom] = nilai_kolom

        # proyeksi disimpan RELATIF terhadap tahun terakhir (tahun+1, tahun+2, ...)
        # supaya kolomnya konsisten antar indikator meski tahun datanya beda-beda
        for i, (tahun_target, nilai_proyeksi) in enumerate(fit["proyeksi"].items(), start=1):
            baris[f"tahun_+{i}"] = tahun_target
            baris[f"proyeksi_+{i}"] = nilai_proyeksi

        hasil.append(baris)

    return hasil, None


def main():
    files = list(Path(FOLDER_BERSIH).glob("*.csv"))
    print(f"Total dataset bersih ditemukan: {len(files)}")

    out_dir = Path(FOLDER_OUTPUT)
    out_dir.mkdir(exist_ok=True)

    semua_hasil = []
    dilewati = []

    for f in files:
        try:
            hasil, error = proses_satu_file(f)
        except Exception as e:
            dilewati.append({"file": f.name, "alasan": f"ERROR: {e}"})
            continue

        if error:
            dilewati.append({"file": f.name, "alasan": error})
            continue
        if not hasil:
            dilewati.append({"file": f.name, "alasan": f"tidak ada grup dengan >= {MIN_TITIK_DATA} titik tahun"})
            continue

        semua_hasil.extend(hasil)

    df_hasil = pd.DataFrame(semua_hasil)
    out_path = out_dir / "proyeksi_semua_indikator.csv"
    df_hasil.to_csv(out_path, index=False)

    print("\n" + "=" * 60)
    print(f"Total baris proyeksi dihasilkan: {len(df_hasil)}")
    print(f"(1 baris = 1 kombinasi indikator + wilayah/breakdown)")
    print(f"Tersimpan di: {out_path}")
    print(f"File dilewati: {len(dilewati)}")
    print("=" * 60)

    if dilewati:
        pd.DataFrame(dilewati).to_csv(out_dir / "dilewati.csv", index=False)
        print(f"Detail file yang dilewati: {out_dir / 'dilewati.csv'}")

    if len(df_hasil):
        print("\nContoh 5 hasil proyeksi (tren paling stabil / R^2 tertinggi):")
        cols_preview = ["indikator", "tahun_terakhir", "nilai_terakhir", "arah_tren", "r_squared"]
        cols_preview = [c for c in cols_preview if c in df_hasil.columns]
        print(df_hasil.sort_values("r_squared", ascending=False)[cols_preview].head(5).to_string(index=False))


if __name__ == "__main__":
    main()
