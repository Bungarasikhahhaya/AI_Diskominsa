"""
Generate Insight Otomatis — Modul 3 (Batching Edition)

Struktur folder yang diasumsikan:
    AI Prediksi Tren/
    ├── hasil_proyeksi/
    │   └── proyeksi_semua_indikator.csv   <- hasil dari prediksi_tren.py
    ├── ...
    └── generate_insight.py                <- taruh script ini di sini

Pembaruan (Batching):
Script ini memproses 10 baris data sekaligus dalam 1 request API (Batching). 
Ini memangkas waktu proses dan penggunaan koneksi secara drastis untuk
menghindari error Rate Limit dari Groq.

Cara pakai:
    pip install pandas groq
    export GROQ_API_KEY="gsk_..."                (Linux/Mac)
    set GROQ_API_KEY=gsk_...                     (Windows cmd)
    python generate_insight.py
"""

import os
import time
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # Akan memuat variabel dari file .env secara otomatis

INPUT_CSV = "hasil_proyeksi/proyeksi_semua_indikator.csv"
OUTPUT_CSV = "hasil_proyeksi/proyeksi_dengan_insight.csv"
MODEL = "llama-3.3-70b-versatile" # Kamu bisa ganti ke 'llama-3.1-8b-instant' jika TPM limit sering tercapai
BATCH_SIZE = 10 # Memproses 10 indikator dalam 1 kali request
JEDA_ANTAR_REQUEST = 3.0  # Jeda dinaikkan sedikit karena 1 request sudah memproses 10 baris

SYSTEM_PROMPT = """Kamu adalah asisten yang menerjemahkan hasil analisis statistik menjadi insight singkat berbahasa Indonesia untuk warga umum (bukan ahli statistik).

ATURAN KETAT:
1. Kamu HANYA boleh memakai angka yang diberikan di data. JANGAN menghitung, mengubah, atau menambahkan angka baru.
2. Tulis 1-2 kalimat singkat, bahasa natural, tanpa jargon statistik.
3. Sesuaikan nada bahasa dengan tingkat keandalan data:
   - r_squared >= 0.6 DAN jumlah_titik >= 8: cukup percaya diri ("diproyeksikan akan...")
   - r_squared < 0.3 ATAU jumlah_titik < 5: bahasa hedging ("cenderung...", "namun perlu dicatat...")
4. WAJIB merespons HANYA dengan JSON Object yang memiliki key "insights", berisi array dari hasil masing-masing ID. 
Format Output:
{
  "insights": [
    {"id": "id_dari_input_1", "insight": "teks insight di sini..."},
    {"id": "id_dari_input_2", "insight": "teks insight di sini..."}
  ]
}"""

def buat_prompt_batch(batch_rows):
    """Susun prompt terstruktur JSON dari sekumpulan baris hasil proyeksi."""
    data_list = []
    for idx, row in batch_rows.iterrows():
        arah_map = {"naik": "naik", "turun": "turun", "stabil": "relatif stabil"}
        arah = arah_map.get(row.get("arah_tren", ""), row.get("arah_tren", "-"))

        item = {
            "id": str(idx),
            "indikator": str(row.get('indikator', '-')),
            "wilayah": str(row.get('wilayah', row.get('level_wilayah', '-'))),
            "titik_dipakai": str(row.get('jumlah_titik_dipakai', '-')),
            "nilai_terakhir": str(row.get('nilai_terakhir', '-')),
            "arah": arah,
            "r_squared": str(row.get('r_squared', '-')),
        }
        
        if pd.notna(row.get("tahun_+1")) and pd.notna(row.get("proyeksi_+1")):
            item["proyeksi_1thn_kdpn"] = f"Tahun {int(row['tahun_+1'])}: {row['proyeksi_+1']}"
            
        data_list.append(item)
    
    # Dump JSON array of inputs
    input_json = json.dumps(data_list, indent=2)
    prompt = f"Berikut adalah {len(data_list)} data indikator:\n{input_json}\n\nBuat insight (maks 2 kalimat) untuk masing-masing id berdasarkan aturan system. Output harus dalam format JSON Object murni."
    return prompt

def generate_insight_batch(client, batch_rows):
    prompt = buat_prompt_batch(batch_rows)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        max_tokens=2048,
        temperature=0.3
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
    if not os.path.exists(INPUT_CSV):
        print(f"[!] File input {INPUT_CSV} tidak ditemukan.")
        return
        
    df = pd.read_csv(INPUT_CSV, low_memory=False)
    if "insight_text" not in df.columns:
        df["insight_text"] = None

    if os.path.exists(OUTPUT_CSV):
        df_out = pd.read_csv(OUTPUT_CSV, low_memory=False)
        if "insight_text" in df_out.columns:
            # Pindahkan insight yang sudah ada
            df["insight_text"] = df_out["insight_text"]
    
    Path(OUTPUT_CSV).parent.mkdir(exist_ok=True, parents=True)

    # Identifikasi baris yang belum diproses
    unprocessed_indices = df[df["insight_text"].isna() | (df["insight_text"].astype(str).str.strip() == "")].index.tolist()
    
    total_baris = len(df)
    baris_selesai = total_baris - len(unprocessed_indices)
    print(f"Total baris: {total_baris} | Sudah diproses: {baris_selesai} | Sisa: {len(unprocessed_indices)}")

    if len(unprocessed_indices) == 0:
        print("Semua data sudah memiliki insight. Selesai.")
        return

    # Buat Batch Array (Daftar potongan index per batch)
    batches = [unprocessed_indices[i:i + BATCH_SIZE] for i in range(0, len(unprocessed_indices), BATCH_SIZE)]
    
    gagal = 0
    for i, batch_indices in enumerate(batches):
        print(f"\n  ... processing batch {i+1}/{len(batches)} (Isi: {len(batch_indices)} indikator)")
        batch_rows = df.loc[batch_indices]
        
        retry = True
        retry_count = 0
        while retry and retry_count < 3:
            retry = False
            try:
                hasil_json_str = generate_insight_batch(client, batch_rows)
                
                try:
                    hasil_json = json.loads(hasil_json_str)
                    insights_list = hasil_json.get("insights", [])
                except json.JSONDecodeError:
                    print("    [Error] AI tidak merespons dengan JSON yang valid. Mencoba ulang...")
                    retry = True
                    retry_count += 1
                    time.sleep(2)
                    continue

                for item in insights_list:
                    row_id = int(item.get("id", -1))
                    if row_id in batch_indices:
                        df.at[row_id, "insight_text"] = item.get("insight", "")
                
                df.to_csv(OUTPUT_CSV, index=False)
                print(f"    [OK] Batch {i+1} tersimpan.")
                
            except Exception as e:
                # Menangani Rate limit
                if "429" in str(e) or "rate_limit" in str(e).lower() or "tokens" in str(e).lower() or "too_many_requests" in str(e).lower():
                    current_key_idx += 1
                    if current_key_idx < len(api_keys):
                        print(f"    [Limit/Token] Key ke-{current_key_idx} habis. Ganti ke Key ke-{current_key_idx + 1}...")
                        client = groq.Groq(api_key=api_keys[current_key_idx])
                        retry = True  # Ulangi dengan key baru
                    else:
                        print(f"    [Error] SEMUA {len(api_keys)} API KEY sudah terkena limit di batch {i+1}.")
                        df.to_csv(OUTPUT_CSV, index=False)
                        print("    Program dihentikan karena Rate Limit. Silakan jalankan lagi beberapa menit kemudian.")
                        return 
                else:
                    print(f"    [Error] pada batch {i+1}: {e}")
                    retry_count += 1
                    if retry_count < 3:
                        print(f"    [Retry] Mencoba ulang batch... ({retry_count}/3)")
                        retry = True
                        time.sleep(2)
                    else:
                        print("    [Gagal] Melewati batch ini setelah 3 kali gagal.")
                        gagal += len(batch_indices)

        # Jeda hanya saat berhasil atau error yang di-skip
        if not retry:
            time.sleep(JEDA_ANTAR_REQUEST)

    # Simpan final
    df.to_csv(OUTPUT_CSV, index=False)

    print("\n" + "=" * 60)
    print(f"Selesai! Baris gagal: {gagal}")
    print(f"Tersimpan di: {OUTPUT_CSV}")
    print("=" * 60)

if __name__ == "__main__":
    main()
