import uuid
import chromadb
import math

from services.query_processor import normalize_question

# =====================================================
# Membuat / Membuka ChromaDB
# =====================================================

client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_or_create_collection(
    name="aceh_statistics"
)

# =====================================================
# Field yang tidak perlu disimpan
# =====================================================

IGNORE_FIELDS = {

    "id",
    "uuid",

    "created_at",
    "updated_at",
    "deleted_at",

    "bps_kode_provinsi",
    "kemendagri_kode_provinsi",

    "bps_kode_kabupaten_kota",
    "kemendagri_kode_kabupaten_kota",

    "bps_kode_kecamatan",
    "kemendagri_kode_kecamatan",

    "bps_kode_desa",
    "kemendagri_kode_desa"

}

# =====================================================
# Membersihkan nilai metadata
# =====================================================

def clean_metadata_value(value):
    """
    ChromaDB hanya menerima metadata bertipe:
    str, int, float, bool
    """

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

    if value == "":
        return None

    if value.lower() == "none":
        return None

    if value.lower() == "nan":
        return None

    return value

# =====================================================
# Build Metadata
# =====================================================
def build_metadata(
    row,
    title,
    identifier,
    document_number,
    dataset_url=None
):

    metadata = {
        "dataset": title,
        "identifier": identifier,
        "document_number": str(document_number)
    }

    if dataset_url:
        metadata["url"] = str(dataset_url)

    # -------------------------
    # Provinsi
    # -------------------------

    provinsi = clean_metadata_value(
        row.get("bps_nama_provinsi")
        or row.get("kemendagri_nama_provinsi")
    )

    if provinsi is not None:
        metadata["provinsi"] = provinsi

    # -------------------------
    # Kabupaten/Kota
    # -------------------------

    region = clean_metadata_value(
        row.get("bps_nama_kabupaten_kota")
        or row.get("kemendagri_nama_kabupaten_kota")
    )

    if region is not None:
        metadata["region"] = region

    # -------------------------
    # Kecamatan
    # -------------------------

    kecamatan = clean_metadata_value(
        row.get("bps_nama_kecamatan")
        or row.get("kemendagri_nama_kecamatan")
    )

    if kecamatan is not None:
        metadata["kecamatan"] = kecamatan

    # -------------------------
    # Desa
    # -------------------------

    desa = clean_metadata_value(
        row.get("bps_nama_desa")
        or row.get("kemendagri_nama_desa")
    )

    if desa is not None:
        metadata["desa"] = desa

    # -------------------------
    # Semua kolom lain
    # -------------------------

    for key, value in row.items():

        if key in IGNORE_FIELDS:
            continue

        clean_value = clean_metadata_value(value)

        if clean_value is None:
            continue

        metadata[key] = clean_value

    return metadata

    # ===========================
    # URL Dataset
    # ===========================

    if dataset_url:

        metadata["url"] = dataset_url

    # ===========================
    # Normalisasi wilayah
    # ===========================

    metadata["provinsi"] = (

        row.get("bps_nama_provinsi")

        or row.get("kemendagri_nama_provinsi")

    )

    metadata["region"] = (

        row.get("bps_nama_kabupaten_kota")

        or row.get("kemendagri_nama_kabupaten_kota")

    )

    metadata["kecamatan"] = (

        row.get("bps_nama_kecamatan")

        or row.get("kemendagri_nama_kecamatan")

    )

    metadata["desa"] = (

        row.get("bps_nama_desa")

        or row.get("kemendagri_nama_desa")

    )

    # ===========================
    # Simpan seluruh kolom
    # ===========================

    for key, value in row.items():

        if key in IGNORE_FIELDS:
            continue

        if value is None:
            continue

        value = str(value).strip()

        if value == "":
            continue

        metadata[key] = value

    return metadata


# =====================================================
# Insert Documents
# =====================================================

def insert_documents(
    documents,
    rows,
    title,
    identifier,
    dataset_url=None
):
    """
    Menyimpan dokumen ke ChromaDB.
    """

    if len(documents) == 0:
        return

    ids = []

    metadatas = []

    for i, (document, row) in enumerate(zip(documents, rows)):

        ids.append(str(uuid.uuid4()))

        metadata = build_metadata(
            row=row,
            title=title,
            identifier=identifier,
            document_number=i + 1,
            dataset_url=dataset_url
        )

        metadatas.append(metadata)

    # tampilkan 1 metadata saja
    if metadatas:
        print("=" * 80)
        print("SAMPLE METADATA")
        for key, value in metadatas[0].items():
            print(f"{key} => {type(value)} => {repr(value)}")
        print("=" * 80)

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    

# =====================================================
# Search
# =====================================================

def search_documents(
    query,
    n_results=10
):
    """
    Mencari dokumen yang paling relevan.
    """

    query = normalize_question(query)

    print("=" * 70)
    print("QUERY")
    print(query)
    print("=" * 70)

    return collection.query(

        query_texts=[query],

        n_results=n_results

    )


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

    return collection.count()


# =====================================================
# Preview
# =====================================================

def preview_documents(limit=5):

    data = collection.get()

    total = len(data["ids"])

    print(f"Total Dokumen : {total}")

    print("-" * 80)

    for i in range(min(limit, total)):

        print(f"ID : {data['ids'][i]}")

        print()

        print("Metadata")

        for key, value in data["metadatas"][i].items():

            print(f"{key} : {value}")

        print()

        print("Document")

        print(data["documents"][i][:800])

        print()

        print("-" * 80)


# =====================================================
# Clear Database
# =====================================================

def clear_database():

    try:

        client.delete_collection("aceh_statistics")

    except Exception:

        pass

    global collection

    collection = client.get_or_create_collection(

        name="aceh_statistics"

    )

    print("Semua dokumen berhasil dihapus.")