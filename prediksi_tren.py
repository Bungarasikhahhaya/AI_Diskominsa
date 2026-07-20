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
3. Deteksi & buang outlier ekstrem (berbasis MAD) sebelum fitting -> menangani
   kasus data dengan lompatan nilai tidak wajar akibat inkonsistensi satuan
4. Fit regresi linear sederhana (tahun -> nilai) sebagai baseline tren
5. Proyeksikan nilai 1-3 tahun ke depan, LENGKAP DENGAN interval kepercayaan
   95% (batas bawah/atas) -> dataset dengan titik data sedikit/fluktuatif
   otomatis dapat pita ketidakpastian lebar, bukan garis proyeksi yang
   kelihatan pasti padahal datanya tipis
6. Hitung R^2 sebagai indikator seberapa "rapi" tren-nya (linear vs fluktuatif)

Catatan penting soal regresi linear sebagai baseline:
- Ini BUKAN model paling canggih, tapi paling gampang dijelaskan ke dosen/
  pembimbing dan robust untuk data tahunan yang titiknya sedikit (~5-25 titik).
- Model yang lebih kompleks (Prophet/ARIMA/LSTM) JUSTRU butuh lebih banyak
  data untuk dilatih dengan baik -> untuk data tahunan yang cuma 3-15 titik,
  model kompleks malah lebih rawan overfitting daripada regresi linear.
- R^2 rendah (<0.3) artinya tren historisnya tidak benar-benar linear/naik-turun
  fluktuatif -> proyeksi linear kurang bisa diandalkan untuk kasus itu, script
  akan menandainya di kolom 'catatan', DAN interval kepercayaannya otomatis
  melebar untuk merefleksikan ketidakpastian itu.
- Kalau nanti mau upgrade, tinggal ganti fungsi fit_dan_proyeksi() dengan
  model lain tanpa ubah struktur pipeline lainnya.

Cara pakai:
    pip install pandas numpy scipy
    python prediksi_tren.py
"""

import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

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


def deteksi_outlier(nilai, ambang_mad=3.5):
    """
    Deteksi outlier pakai Median Absolute Deviation (MAD) - lebih tahan
    terhadap outlier ekstrem dibanding metode std-dev biasa (karena std
    sendiri gampang "ketarik" oleh outlier yang mau dideteksi).

    Return: array boolean, True = outlier (harus dibuang sebelum fitting).

    Kasus nyata yang melatarbelakangi ini: dataset dengan lompatan nilai
    ekstrem (misal dari puluhan ribu ke 175 juta lalu jatuh ke ~2) akibat
    inkonsistensi satuan di sumber data. Titik seperti itu bisa merusak
    total garis regresi kalau tidak difilter dulu.
    """
    nilai = np.array(nilai, dtype=float)
    median = np.median(nilai)
    mad = np.median(np.abs(nilai - median))

    if mad == 0:
        # Semua nilai sama/nyaris sama -> tidak ada yang dianggap outlier
        return np.zeros(len(nilai), dtype=bool)

    # faktor 0.6745 mengonversi MAD ke skala setara std-dev (untuk data normal)
    skor_modified_z = 0.6745 * (nilai - median) / mad
    return np.abs(skor_modified_z) > ambang_mad


def fit_dan_proyeksi(tahun, nilai, tahun_ke_depan=TAHUN_KE_DEPAN):
    """
    Fit regresi linear sederhana (numpy polyfit derajat 1) dan proyeksikan
    N tahun ke depan dari titik data terakhir.

    Termasuk:
    - Deteksi & pembuangan outlier sebelum fitting (lihat deteksi_outlier())
    - Interval kepercayaan 95% di sekitar proyeksi (prediction interval),
      supaya dataset dengan titik data sedikit/fluktuatif otomatis dapat
      pita ketidakpastian LEBAR -> jujur soal seberapa yakin sistem,
      bukan cuma satu garis proyeksi yang kelihatan pasti.

    Return dict berisi slope, r_squared, proyeksi per tahun (+interval),
    arah tren, dan info outlier yang dibuang.
    """
    tahun_asli = np.array(tahun, dtype=float)
    nilai_asli = np.array(nilai, dtype=float)

    # --- Deteksi & buang outlier, TAPI hanya kalau sisa datanya masih cukup ---
    outlier_mask = deteksi_outlier(nilai_asli)
    jumlah_outlier = int(outlier_mask.sum())

    if jumlah_outlier > 0 and (len(nilai_asli) - jumlah_outlier) >= MIN_TITIK_DATA:
        tahun_fit = tahun_asli[~outlier_mask]
        nilai_fit = nilai_asli[~outlier_mask]
    else:
        # Kalau buang outlier bikin data kurang dari minimum, tetap pakai semua
        # data (lebih baik proyeksi kasar daripada gagal total)
        tahun_fit = tahun_asli
        nilai_fit = nilai_asli
        jumlah_outlier = 0

    n = len(tahun_fit)
    slope, intercept = np.polyfit(tahun_fit, nilai_fit, 1)
    prediksi_historis = slope * tahun_fit + intercept

    # R^2 (dihitung dari data yang dipakai fitting, setelah outlier dibuang)
    ss_res = np.sum((nilai_fit - prediksi_historis) ** 2)
    ss_tot = np.sum((nilai_fit - np.mean(nilai_fit)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    # --- Standard error & interval kepercayaan 95% untuk prediksi ---
    # Rumus prediction interval regresi linear sederhana:
    #   se_pred(x0) = se_residual * sqrt(1 + 1/n + (x0-mean_x)^2/Sxx)
    # se_pred lebih LEBAR untuk: (a) n kecil, (b) x0 jauh dari data historis
    # (ekstrapolasi jauh ke depan), (c) residual historis besar (fluktuatif).
    derajat_bebas = max(n - 2, 1)
    se_residual = np.sqrt(ss_res / derajat_bebas) if n > 2 else np.nan
    mean_x = np.mean(tahun_fit)
    sxx = np.sum((tahun_fit - mean_x) ** 2)
    t_kritis = stats.t.ppf(0.975, derajat_bebas) if n > 2 else np.nan  # 95% dua sisi

    tahun_terakhir = int(tahun_asli.max())
    proyeksi = {}
    for i in range(1, tahun_ke_depan + 1):
        tahun_target = tahun_terakhir + i
        titik_tengah = slope * tahun_target + intercept

        if n > 2 and sxx > 0:
            se_pred = se_residual * np.sqrt(1 + 1 / n + (tahun_target - mean_x) ** 2 / sxx)
            margin = t_kritis * se_pred
        else:
            # Data terlalu sedikit buat hitung interval yang valid
            margin = np.nan

        proyeksi[tahun_target] = {
            "nilai": round(titik_tengah, 3),
            "batas_bawah": round(titik_tengah - margin, 3) if not np.isnan(margin) else None,
            "batas_atas": round(titik_tengah + margin, 3) if not np.isnan(margin) else None,
        }

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
        "nilai_terakhir": round(nilai_asli[-1], 3),
        "proyeksi": proyeksi,
        "jumlah_outlier_dibuang": jumlah_outlier,
        "jumlah_titik_dipakai": n,
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

        catatan_list = []
        if fit["r_squared"] < 0.3:
            catatan_list.append("Tren historis fluktuatif (R^2 rendah) - proyeksi linear kurang bisa diandalkan")
        elif fit["r_squared"] < 0.6:
            catatan_list.append("Tren historis cukup fluktuatif - proyeksi linear sebagai estimasi kasar")
        if fit["jumlah_outlier_dibuang"] > 0:
            catatan_list.append(
                f"{fit['jumlah_outlier_dibuang']} titik terdeteksi sebagai outlier ekstrem dan "
                f"dikeluarkan dari perhitungan tren (kemungkinan inkonsistensi satuan/input di sumber data)"
            )
        if fit["jumlah_titik_dipakai"] < 5:
            catatan_list.append("Titik data historis sedikit - interval kepercayaan lebar / proyeksi kurang presisi")
        catatan = " | ".join(catatan_list)

        baris = {
            "file_sumber": path_csv.name,
            "indikator": path_csv.stem,
            "level_wilayah": level_wilayah,
            "satuan": satuan,
            "jumlah_titik_tahun": len(grup),
            "jumlah_titik_dipakai": fit["jumlah_titik_dipakai"],
            "jumlah_outlier_dibuang": fit["jumlah_outlier_dibuang"],
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
        # supaya kolomnya konsisten antar indikator meski tahun datanya beda-beda.
        # Termasuk batas bawah/atas interval kepercayaan 95%.
        for i, (tahun_target, detail) in enumerate(fit["proyeksi"].items(), start=1):
            baris[f"tahun_+{i}"] = tahun_target
            baris[f"proyeksi_+{i}"] = detail["nilai"]
            baris[f"proyeksi_+{i}_bawah"] = detail["batas_bawah"]
            baris[f"proyeksi_+{i}_atas"] = detail["batas_atas"]

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
