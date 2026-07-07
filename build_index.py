import json
import os
import pandas as pd

from services.catalog import get_catalog
from services.api_client import get_dataset
from services.preprocess import convert_to_documents
from services.vectordb import insert_documents

# ==========================
# Konfigurasi
# ==========================

INDEX_FILE = "indexed_datasets.json"
CSV_FOLDER = "data/csv"

os.makedirs(CSV_FOLDER, exist_ok=True)


# ==========================
# Membaca dataset yang sudah di-index
# ==========================

def load_indexed():

    if not os.path.exists(INDEX_FILE):
        return set()

    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:

            content = f.read().strip()

            if not content:
                return set()

            return set(json.loads(content))

    except Exception:

        return set()


# ==========================
# Menyimpan dataset yang sudah di-index
# ==========================

def save_indexed(indexed):

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(
            list(indexed),
            f,
            indent=4,
            ensure_ascii=False
        )


# ==========================
# Menyimpan CSV
# ==========================

def save_csv(title, rows):

    filename = "".join(
        c if c.isalnum() else "_"
        for c in title
    )

    filepath = os.path.join(
        CSV_FOLDER,
        filename + ".csv"
    )

    df = pd.DataFrame(rows)

    df.to_csv(
        filepath,
        index=False,
        encoding="utf-8-sig"
    )

    return filepath


# ==========================
# Build Index
# ==========================

def build_index():

    catalog = get_catalog()

    indexed = load_indexed()

    total_dataset = len(catalog)

    print("=" * 80)
    print(f"Total Dataset            : {total_dataset}")
    print(f"Sudah Pernah Di-index    : {len(indexed)}")
    print("=" * 80)

    total_document = 0
    success = 0
    failed = 0
    skipped = 0

    for i, dataset in enumerate(catalog, start=1):

        title = dataset.get("title", "Tanpa Judul")
        description = dataset.get("description", "")
        identifier = dataset.get("identifier")

        print("\n" + "-" * 80)
        print(f"[{i}/{total_dataset}] {title}")

        if not identifier:

            print("❌ Identifier tidak ditemukan.")

            failed += 1

            continue

        if identifier in indexed:

            print("⏩ Dataset sudah pernah di-index.")

            skipped += 1

            continue

        try:

            api_response = get_dataset(identifier)

            if api_response is None:

                print("❌ Gagal mengambil API.")

                failed += 1

                continue

            rows = api_response.get(
                "data",
                {}
            ).get(
                "rows",
                []
            )

            if len(rows) == 0:

                print("⚠ Dataset kosong.")

                continue

            # ======================
            # Simpan CSV
            # ======================

            csv_file = save_csv(
                title,
                rows
            )

            print(f"💾 CSV : {csv_file}")

            # ======================
            # Convert ke document
            # ======================

            documents = convert_to_documents(
                title,
                description,
                api_response
            )

            # ======================
            # Simpan ke ChromaDB
            # ======================

            insert_documents(
                documents,
                title,
                identifier
            )

            total_document += len(documents)

            success += 1

            indexed.add(identifier)

            save_indexed(indexed)

            print(f"✅ Dokumen dibuat : {len(documents)}")
            print(f"📄 Total dokumen : {total_document}")

        except Exception as e:

            failed += 1

            print("❌ ERROR")

            print(e)

    print("\n")
    print("=" * 80)
    print("INDEXING SELESAI")
    print("=" * 80)
    print(f"Berhasil        : {success}")
    print(f"Gagal           : {failed}")
    print(f"Dilewati        : {skipped}")
    print(f"Total Dokumen   : {total_document}")
    print("=" * 80)


if __name__ == "__main__":
    build_index()