import requests
import json
import sys
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from supabase import Client, create_client

try:
    from google import genai
except ImportError:
    genai = None

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_PATH)

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
SATUDATA_KEY = os.getenv("SATUDATA_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

if not SATUDATA_KEY:
    print("ERROR: SATUDATA_API_KEY tidak ditemukan di .env")
    sys.exit(1)
if not GEMINI_KEY:
    print("ERROR: GEMINI_API_KEY tidak ditemukan di .env")
    sys.exit(1)
if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
    print("ERROR: SUPABASE_URL atau SUPABASE_SECRET_KEY tidak ditemukan di .env")
    sys.exit(1)
if genai is None:
    print("ERROR: library 'google-genai' belum ke-install. Jalankan: pip install google-genai")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
MODEL_NAME = "gemini-3.5-flash"

BASE_URL = "https://satudata.acehprov.go.id/api/v1.1"
headers = {"APIKEY": SATUDATA_KEY}

FIELD_METADATA = {
    "bps_kode_provinsi", "bps_nama_provinsi", "kemendagri_kode_provinsi", "kemendagri_nama_provinsi",
    "bps_kode_kabupaten_kota", "bps_nama_kabupaten_kota", "kemendagri_kode_kabupaten_kota", "kemendagri_nama_kabupaten_kota",
    "bps_kode_kecamatan", "bps_nama_kecamatan", "kemendagri_kode_kecamatan", "kemendagri_nama_kecamatan",
    "bps_kode_desa", "bps_nama_desa", "kemendagri_kode_desa", "kemendagri_nama_desa",
    "tahun", "tingkat_penyajian", "created_at", "updated_at", "deleted_at", "id", "uuid", "satuan"
}


def cari_dataset(kata_kunci: str, limit: int = 5, page: int = 0) -> list:
    resp = requests.get(f"{BASE_URL}/datasets/list/",
                         params={"limit": limit, "page": page, "search": kata_kunci},
                         headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()["data"]["rows"]


def simpan_katalog(dataset_list: list) -> int:
    payload = [
        {"uuid": dataset["uuid"], "judul": dataset["judul"]}
        for dataset in dataset_list
        if dataset.get("uuid") and dataset.get("judul")
    ]
    if payload:
        supabase.table("dataset_katalog").upsert(payload, on_conflict="uuid").execute()
    return len(payload)


def baca_katalog() -> list:
    response = supabase.table("dataset_katalog").select("uuid,judul").order("judul").execute()
    return response.data or []


def sinkronkan_katalog(limit: int = 500) -> list:
    """Mengambil semua halaman katalog Satu Data Aceh dan menyimpannya ke Supabase."""
    page = 0
    while True:
        dataset_list = cari_dataset("", limit=limit, page=page)
        if not dataset_list:
            break

        simpan_katalog(dataset_list)
        if len(dataset_list) < limit:
            break
        page += 1

    return baca_katalog()


def ambil_data_source(uuid: str, tahun: Optional[int] = None) -> list:
    params = {"tahun": tahun} if tahun is not None else {}
    resp = requests.get(f"{BASE_URL}/datasets/datasource/{uuid}/",
                         params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()["data"]["rows"]


def ekstrak_nilai_indikator(baris: dict) -> dict:
    hasil = {k: v for k, v in baris.items() if k not in FIELD_METADATA and v is not None}
    hasil["wilayah"] = (baris.get("bps_nama_kabupaten_kota") or baris.get("tingkat_penyajian")
                         or baris.get("bps_nama_provinsi") or "Aceh")
    hasil["tahun"] = baris.get("tahun")
    return hasil


def susun_narasi(dataset_data: list[dict]) -> str:
    judul_dataset = ", ".join(dataset["judul"] for dataset in dataset_data)
    prompt = f"""Kamu adalah penulis laporan statistik resmi untuk UPTD Statistik Pemerintah Aceh.

Susun satu narasi laporan terpadu (2-4 paragraf) dari dataset berikut: "{judul_dataset}". WAJIB:
- Semua angka harus PERSIS sesuai data, jangan dibulatkan/diubah/ditebak.
- Sebutkan wilayah dan tahun datanya.
- Jika ada beberapa dataset, jelaskan masing-masing dataset secara runtut dan hanya buat perbandingan bila indikatornya memang sebanding.
- Gaya bahasa formal, seperti laporan resmi pemerintah.

DATA:
{json.dumps(dataset_data, ensure_ascii=False, indent=2)}
"""
    respon = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return respon.text


# ============ FASTAPI ============
app = FastAPI(title="API Narasi Laporan Statistik Aceh")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # sementara dibuka semua, nanti dipersempit ke domain frontend
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/narasi")
def get_narasi(
    uuid: list[str] = Query(..., min_length=1),
    judul: list[str] = Query(default=[]),
):
    """Menyusun narasi dari satu atau beberapa UUID dataset tanpa membatasi tahun."""
    dataset_data = []
    dataset_tidak_ada = []

    judul_per_uuid = dict(zip(uuid, judul))
    for dataset_uuid in dict.fromkeys(uuid):
        baris_data = ambil_data_source(dataset_uuid)
        data_bersih = [ekstrak_nilai_indikator(baris) for baris in baris_data]

        if not data_bersih:
            dataset_tidak_ada.append(dataset_uuid)
            continue

        dataset_data.append({
            "uuid": dataset_uuid,
            "judul": judul_per_uuid.get(dataset_uuid) or f"Dataset {dataset_uuid}",
            "data": data_bersih,
        })

    if not dataset_data:
        return {
            "judul": "Narasi laporan",
            "dataset": [],
            "narasi": None,
            "pesan": "Data tidak tersedia untuk dataset yang dipilih."
        }

    narasi = susun_narasi(dataset_data)
    judul = "Narasi gabungan: " + ", ".join(dataset["judul"] for dataset in dataset_data)
    pesan = None
    if dataset_tidak_ada:
        pesan = f"Data tidak tersedia untuk {len(dataset_tidak_ada)} dataset; narasi dibuat dari dataset yang memiliki data."

    return {
        "judul": judul,
        "dataset": [{"uuid": dataset["uuid"], "judul": dataset["judul"]} for dataset in dataset_data],
        "data": dataset_data,
        "narasi": narasi,
        "pesan": pesan
    }


@app.get("/dataset")
def get_dataset():
    try:
        katalog = baca_katalog()
        return katalog if katalog else sinkronkan_katalog()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Katalog dataset Supabase belum tersedia. Pastikan tabel sudah dibuat dan portal Satu Data Aceh dapat diakses.") from exc


@app.post("/dataset/sinkronkan")
def post_sinkronkan_dataset():
    """Memperbarui katalog dropdown dari Satu Data Aceh."""
    try:
        katalog = sinkronkan_katalog()
        return {"jumlah": len(katalog), "dataset": katalog}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Gagal menyinkronkan katalog ke Supabase.") from exc


@app.get("/cari-dataset")
def get_cari_dataset(kata_kunci: str, limit: int = 5):
    """Buat bantu cari nama dataset yang tepat sebelum panggil /narasi"""
    return cari_dataset(kata_kunci, limit)


@app.get("/tahun-dataset")
def get_tahun_dataset(uuid: str):
    """Mengembalikan hanya tahun yang benar-benar tersedia pada suatu dataset."""
    baris_data = ambil_data_source(uuid)
    tahun_tersedia = sorted(
        {int(baris["tahun"]) for baris in baris_data if baris.get("tahun") is not None},
        reverse=True,
    )
    if not tahun_tersedia:
        raise HTTPException(status_code=404, detail="Tahun data tidak ditemukan untuk dataset ini")
    return {"uuid": uuid, "tahun": tahun_tersedia}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
