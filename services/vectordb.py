import uuid
import chromadb

# =====================================
# Membuat / Membuka ChromaDB
# =====================================

client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_or_create_collection(
    name="aceh_statistics"
)


# =====================================
# Insert Document
# =====================================

def insert_documents(documents, title, identifier):

    if not documents:
        return

    ids = []
    metadatas = []

    for i, doc in enumerate(documents):

        ids.append(str(uuid.uuid4()))

        metadatas.append({
            "dataset": title,
            "identifier": identifier,
            "document_number": i + 1
        })

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )


# =====================================
# Search
# =====================================

def search_documents(query, n_results=5):

    return collection.query(
        query_texts=[query],
        n_results=n_results
    )


# =====================================
# Jumlah Dokumen
# =====================================

def count_documents():

    return collection.count()


# =====================================
# Menampilkan beberapa dokumen
# =====================================

def preview_documents(limit=5):

    data = collection.get()

    total = len(data["ids"])

    print(f"Total Dokumen : {total}")

    print("-" * 60)

    for i in range(min(limit, total)):

        print(f"ID : {data['ids'][i]}")

        print(data["documents"][i])

        print(data["metadatas"][i])

        print("-" * 60)


# =====================================
# Hapus seluruh database
# =====================================

def clear_database():

    client.delete_collection("aceh_statistics")

    global collection

    collection = client.get_or_create_collection(
        name="aceh_statistics"
    )

    print("Semua dokumen berhasil dihapus.")