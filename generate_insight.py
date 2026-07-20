"""
Generate Insight Otomatis — Modul 3

Struktur folder yang diasumsikan:
    AI Prediksi Tren/
    ├── hasil_proyeksi/
    │   └── proyeksi_semua_indikator.csv   <- hasil dari prediksi_tren.py
    ├── ...
    └── generate_insight.py                <- taruh script ini di sini

Untuk SETIAP baris di proyeksi_semua_indikator.csv (1 baris = 1 kombinasi
indikator + wilayah), script ini memanggil Claude API untuk menghasilkan
1-2 kalimat insight dalam bahasa manusia, lalu menyimpan hasilnya sebagai
kolom baru 'insight_text'.

PRINSIP PENTING: LLM di sini HANYA merangkai kalimat dari angka yang sudah
final (hasil regresi linear di prediksi_tren.py). LLM TIDAK diminta
menghitung ulang tren atau proyeksi apapun -> supaya angka yang ditampilkan
selalu konsisten antara grafik dan narasi, dan tidak ada risiko halusinasi
angka.

Nada bahasa insight otomatis disesuaikan dengan kualitas data (r_squared,
jumlah titik data, ada-tidaknya outlier yang dibuang):
- R^2 tinggi & titik data banyak -> bahasa cukup percaya diri
- R^2 rendah / titik data sedikit -> bahasa hedging, tekankan ketidakpastian

CACHING: insight cuma di-generate SEKALI per baris, disimpan ke CSV.
Jangan panggil API ini tiap kali dashboard diakses user -> mahal & lambat.
Jalankan ulang script ini cuma waktu pipeline data di-refresh.

Cara pakai:
    pip install pandas groq
    export GROQ_API_KEY="gsk_..."                (Linux/Mac)
    set GROQ_API_KEY=gsk_...                     (Windows cmd)
    $env:GROQ_API_KEY="gsk_..."                  (Windows PowerShell)
    python generate_insight.py
"""

import os
import time
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # Akan memuat variabel dari file .env secara otomatis

INPUT_CSV = "hasil_proyeksi/proyeksi_semua_indikator.csv"
OUTPUT_CSV = "hasil_proyeksi/proyeksi_dengan_insight.csv"
MODEL = "llama-3.3-70b-versatile"
JEDA_ANTAR_REQUEST = 2.0  # detik, disesuaikan agar tidak kena rate limit groq


SYSTEM_PROMPT = """Kamu adalah asisten yang menerjemahkan hasil analisis statistik
menjadi insight singkat berbahasa Indonesia untuk warga umum (bukan ahli statistik).

ATURAN KETAT:
1. Kamu HANYA boleh memakai angka yang diberikan di data. JANGAN menghitung,
   mengubah, atau menambahkan angka baru yang tidak ada di input.
2. Tulis 2 kalimat singkat, bahasa natural, tanpa jargon statistik (jangan
   pakai kata "R-squared", "regresi", "outlier" - jelaskan maknanya secara
   natural kalau perlu).
3. Sesuaikan nada bahasa dengan tingkat keandalan data:
   - Kalau r_squared >= 0.6 DAN jumlah_titik_dipakai >= 8: boleh bahasa
     cukup percaya diri ("diproyeksikan akan...", "menunjukkan tren...")
   - Kalau r_squared < 0.3 ATAU jumlah_titik_dipakai < 5: WAJIB pakai bahasa
     hedging yang jelas ("cenderung...", "namun perlu dicatat data historis
     cukup bervariasi sehingga angka ini sebaiknya dilihat sebagai perkiraan
     kasar, bukan kepastian")
   - Di antara itu: nada netral, sebutkan ada ketidakpastian secukupnya
4. Kalau ada outlier yang dibuang (jumlah_outlier_dibuang > 0), boleh
   disinggung sekilas kalau relevan (misal "beberapa data tidak konsisten
   sehingga dikecualikan dari perhitungan").
5. Jangan mengarang penyebab tren (jangan bilang "karena kebijakan X" atau
   semacamnya) kecuali benar-benar tersirat jelas dari nama indikatornya.
6. Output HANYA teks insight-nya saja, tanpa embel-embel seperti "Berikut
   insight-nya:" atau tanda kutip."""


def buat_prompt(row):
    """Susun prompt terstruktur dari 1 baris hasil proyeksi."""
    arah_map = {"naik": "naik", "turun": "turun", "stabil": "relatif stabil"}
    arah = arah_map.get(row.get("arah_tren", ""), row.get("arah_tren", "-"))

    bagian = [
        f"Indikator: {row.get('indikator', '-')}",
        f"Wilayah: {row.get('wilayah', row.get('level_wilayah', '-'))}",
        f"Satuan: {row.get('satuan', '-')}",
        f"Jumlah titik data historis yang dipakai: {row.get('jumlah_titik_dipakai', '-')}",
        f"Tahun terakhir data: {row.get('tahun_terakhir', '-')}",
        f"Nilai terakhir: {row.get('nilai_terakhir', '-')}",
        f"Arah tren: {arah}",
        f"R-squared (keandalan tren, skala 0-1): {row.get('r_squared', '-')}",
        f"Jumlah outlier yang dibuang dari perhitungan: {row.get('jumlah_outlier_dibuang', 0)}",
    ]

    if pd.notna(row.get("tahun_+1")) and pd.notna(row.get("proyeksi_+1")):
        bagian.append(
            f"Proyeksi tahun {int(row['tahun_+1'])}: {row['proyeksi_+1']} "
            f"(rentang kemungkinan: {row.get('proyeksi_+1_bawah', '-')} "
            f"sampai {row.get('proyeksi_+1_atas', '-')})"
        )

    bagian.append("\nBuat insight singkat (2 kalimat) berdasarkan data di atas.")
    return "\n".join(bagian)


def generate_insight_satu_baris(client, row):
    prompt = buat_prompt(row)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


def main():
    api_keys_str = os.environ.get("GROQ_API_KEYS") or os.environ.get("GROQ_API_KEY")
    if not api_keys_str:
        print("[!] GROQ_API_KEYS (atau GROQ_API_KEY) belum di-set di .env.")
        return

    api_keys = [k.strip() for k in api_keys_str.split(",") if k.strip()]
    current_key_idx = 0

    import groq
    client = groq.Groq(api_key=api_keys[current_key_idx])

    # Mekanisme Resume
    df = pd.read_csv(INPUT_CSV, low_memory=False)
    if "insight_text" not in df.columns:
        df["insight_text"] = None

    if os.path.exists(OUTPUT_CSV):
        df_out = pd.read_csv(OUTPUT_CSV, low_memory=False)
        if "insight_text" in df_out.columns:
            # Pindahkan insight yang sudah selesai ke df utama
            df["insight_text"] = df_out["insight_text"]
    
    Path(OUTPUT_CSV).parent.mkdir(exist_ok=True, parents=True)

    total_baris = len(df)
    baris_sudah = df["insight_text"].notna().sum()
    
    # Hitung yang insight_text-nya bukan string kosong
    baris_selesai = 0
    for val in df["insight_text"]:
        if pd.notna(val) and str(val).strip() != "":
            baris_selesai += 1
            
    print(f"Total baris: {total_baris} | Sudah diproses: {baris_selesai} | Sisa: {total_baris - baris_selesai}")

    gagal = 0
    for i, row in df.iterrows():
        # Lewati jika baris ini sudah ada insight-nya (Resume)
        if pd.notna(row.get("insight_text")) and str(row.get("insight_text")).strip() != "":
            continue

        if (i + 1) % 10 == 0 or (i + 1) == total_baris:
            print(f"  ... progress: {i + 1}/{total_baris}")

        retry = True
        while retry:
            retry = False
            try:
                teks = generate_insight_satu_baris(client, row)
                df.at[i, "insight_text"] = teks
                
                # Simpan setiap 10 baris agar tidak hilang jika script terhenti/error
                if (i + 1) % 10 == 0:
                    df.to_csv(OUTPUT_CSV, index=False)
                    
            except Exception as e:
                # Cek jika error karena rate limit (429)
                if "429" in str(e) or "rate_limit" in str(e).lower() or "tokens" in str(e).lower():
                    current_key_idx += 1
                    if current_key_idx < len(api_keys):
                        print(f"    [Limit] API Key ke-{current_key_idx} habis. Ganti ke API Key ke-{current_key_idx + 1}...")
                        client = groq.Groq(api_key=api_keys[current_key_idx])
                        retry = True  # Ulangi baris ini dengan API key baru
                    else:
                        print(f"    [Error] SEMUA {len(api_keys)} API KEY sudah terkena limit di baris {i}.")
                        df.to_csv(OUTPUT_CSV, index=False)
                        return  # Berhenti eksekusi dan keluar (jangan paksa error)
                else:
                    gagal += 1
                    df.at[i, "insight_text"] = ""
                    print(f"    [Error] baris {i} ({row.get('indikator', '-')}): {e}")

        # Jeda hanya saat berhasil atau error non-limit
        if not retry:
            time.sleep(JEDA_ANTAR_REQUEST)

    # Simpan final
    df.to_csv(OUTPUT_CSV, index=False)

    print("\n" + "=" * 60)
    print(f"Selesai. Insight baru berhasil: {total_baris - baris_selesai - gagal} | Gagal (Bukan Limit): {gagal}")
    print(f"Tersimpan di: {OUTPUT_CSV}")
    print("=" * 60)


if __name__ == "__main__":
    main()
