import math
# pyrefly: ignore [missing-import]
from supabase import create_client, Client
from langchain_huggingface import HuggingFaceEmbeddings
from config import SUPABASE_URL, SUPABASE_SECRET_KEY, GOOGLE_API_KEY
from services.query_processor import normalize_question

# =====================================================
# Supabase & Embeddings Initialization
# =====================================================

if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
    print("WARNING: SUPABASE_URL atau SUPABASE_SECRET_KEY tidak diset.")
    
supabase: Client = create_client(SUPABASE_URL or "", SUPABASE_SECRET_KEY or "")

# Menggunakan model lokal (dimensi 384) persis seperti bawaan ChromaDB
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

# =====================================================
# Field yang tidak perlu disimpan
# =====================================================

IGNORE_FIELDS = {
    "id", "uuid",
    "created_at", "updated_at", "deleted_at",
    "bps_kode_provinsi", "kemendagri_kode_provinsi",
    "bps_kode_kabupaten_kota", "kemendagri_kode_kabupaten_kota",
    "bps_kode_kecamatan", "kemendagri_kode_kecamatan",
    "bps_kode_desa", "kemendagri_kode_desa"
}

# =====================================================
# Membersihkan nilai metadata
# =====================================================

def clean_metadata_value(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if math.isnan(value):
            return None
        return value

    value = str(value).strip()
    if value == "" or value.lower() in ("none", "nan"):
        return None

    return value

# =====================================================
# Build Metadata
# =====================================================

def build_metadata(row, title, identifier, document_number, dataset_url=None):
    metadata = {
        "dataset": title,
        "identifier": identifier,
        "document_number": str(document_number)
    }

    if dataset_url:
        metadata["url"] = str(dataset_url)

    provinsi = clean_metadata_value(row.get("bps_nama_provinsi") or row.get("kemendagri_nama_provinsi"))
    if provinsi: metadata["provinsi"] = provinsi

    region = clean_metadata_value(row.get("bps_nama_kabupaten_kota") or row.get("kemendagri_nama_kabupaten_kota"))
    if region: metadata["region"] = region

    kecamatan = clean_metadata_value(row.get("bps_nama_kecamatan") or row.get("kemendagri_nama_kecamatan"))
    if kecamatan: metadata["kecamatan"] = kecamatan

    desa = clean_metadata_value(row.get("bps_nama_desa") or row.get("kemendagri_nama_desa"))
    if desa: metadata["desa"] = desa

    for key, value in row.items():
        if key in IGNORE_FIELDS:
            continue
        clean_value = clean_metadata_value(value)
        if clean_value is None:
            continue
        # pastikan semua di cast ke string (Supabase jsonb bisa terima apapun, tapi ini menjaga konsistensi dengan Chroma sebelumnya)
        metadata[key] = str(clean_value)

    return metadata

# =====================================================
# Insert Documents
# =====================================================

def insert_documents(documents, rows, title, identifier, dataset_url=None):
    """Menyimpan dokumen ke Supabase (pgvector)."""
    if len(documents) == 0:
        return

    # Generate embeddings untuk batch dokumen
    try:
        doc_embeddings = embeddings.embed_documents(documents)
    except Exception as e:
        print(f"Gagal membuat embedding: {e}")
        raise e

    records = []
    for i, (doc, row, emb) in enumerate(zip(documents, rows, doc_embeddings)):
        metadata = build_metadata(
            row=row, title=title, identifier=identifier,
            document_number=i + 1, dataset_url=dataset_url
        )
        
        # Ekstrak nilai spesifik untuk kolom tersendiri
        dataset_val = title
        identifier_val = identifier
        
        tahun_val = None
        for key in ["tahun", "waktu", "year", "periode"]:
            if key in row and row[key]:
                try:
                    tahun_val = int(row[key])
                    break
                except ValueError:
                    pass
                    
        wilayah_val = metadata.get("region") or metadata.get("provinsi") or metadata.get("kecamatan") or metadata.get("desa") or None
        
        records.append({
            "dataset": dataset_val,
            "identifier": identifier_val,
            "tahun": tahun_val,
            "wilayah": wilayah_val,
            "document": doc,
            "metadata": metadata,
            "embedding": emb
        })

    # tampilkan 1 sampel
    if records:
        print("=" * 80)
        print("SAMPLE METADATA")
        for key, value in records[0]["metadata"].items():
            print(f"{key} => {type(value)} => {repr(value)}")
        print("=" * 80)

    # Insert ke tabel Supabase (batching opsional jika terlalu besar, tapi Supabase bisa handle ratusan row sekaligus)
    BATCH_SIZE = 100
    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        try:
            supabase.table("aceh_statistics").insert(batch).execute()
        except Exception as e:
            print(f"Gagal insert ke Supabase: {e}")

# =====================================================
# Search
# =====================================================

def search_documents(query, n_results=10):
    """Mencari dokumen yang paling relevan menggunakan pgvector RPC."""
    query_norm = normalize_question(query)

    print("=" * 70)
    print("QUERY")
    print(query_norm)
    print("=" * 70)

    try:
        query_embedding = embeddings.embed_query(query_norm)
    except Exception as e:
        print(f"Gagal embed query: {e}")
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    # Panggil fungsi RPC 'match_documents' di Supabase
    try:
        response = supabase.rpc("match_documents", {
            "query_embedding": query_embedding,
            "match_count": n_results
        }).execute()
        
        results = response.data
    except Exception as e:
        print(f"Gagal mencari di Supabase: {e}")
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    # Format kembali seperti ChromaDB output
    docs = []
    metas = []
    dists = []
    
    for r in results:
        docs.append(r.get("document", ""))
        metas.append(r.get("metadata", {}))
        # RPC mengembalikan similarity (0 sampai 1), kita ubah ke distance (1 - similarity)
        similarity = r.get("similarity", 0)
        dists.append(1 - similarity)

    return {
        "documents": [docs],
        "metadatas": [metas],
        "distances": [dists]
    }

# =====================================================
# Show Results
# =====================================================

def show_results(result):
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    if len(documents) == 0:
        print("Tidak ada dokumen ditemukan.")
        return

    for i in range(len(documents)):
        print("=" * 80)
        print(f"HASIL {i+1}")
        print(f"Distance : {distances[i]:.4f}")
        print()
        print("Metadata")
        for key, value in metadatas[i].items():
            print(f"{key} : {value}")
        print()
        print("-" * 80)
        print(documents[i][:800])
        print()

# =====================================================
# Count
# =====================================================

def count_documents():
    try:
        res = supabase.table("aceh_statistics").select("id", count="exact").limit(1).execute()
        return res.count
    except Exception:
        return 0

# =====================================================
# Preview
# =====================================================

def preview_documents(limit=5):
    try:
        res = supabase.table("aceh_statistics").select("*").limit(limit).execute()
        data = res.data
    except Exception as e:
        print(f"Gagal preview: {e}")
        return
        
    total = count_documents()
    print(f"Total Dokumen (Approx) : {total}")
    print("-" * 80)

    for i, row in enumerate(data):
        print(f"ID : {row.get('id')}")
        print()
        print("Metadata")
        for key, value in (row.get("metadata") or {}).items():
            print(f"{key} : {value}")
        print()
        print("Document")
        print(str(row.get("document", ""))[:800])
        print()
        print("-" * 80)

# =====================================================
# Clear Database
# =====================================================

def clear_database():
    try:
        # Menghapus semua data (hanya jika ada RLS policy yang mengizinkan atau menggunakan service role)
        # Atau bisa pakai fungsi rpc untuk delete all
        # Di sini kita mencoba delete dengan match tidak kosong
        supabase.table("aceh_statistics").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("Semua dokumen berhasil dihapus dari Supabase.")
    except Exception as e:
        print(f"Gagal menghapus dokumen: {e}")