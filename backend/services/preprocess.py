"""
Preprocessing data sebelum dimasukkan ke ChromaDB
"""

# =====================================
# Field yang tidak digunakan
# =====================================

IGNORE_FIELDS = {
    "id",
    "uuid",
    "created_at",
    "updated_at",
    "bps_kode_provinsi",
    "kemendagri_kode_provinsi"
}


# =====================================
# Membersihkan nama kolom
# =====================================

def clean_key(key):
    """
    Mengubah nama kolom menjadi lebih mudah dibaca.
    Contoh:
    jumlah_penduduk -> Jumlah Penduduk
    """

    return key.replace("_", " ").title()


# =====================================
# Mengubah satu baris data menjadi dokumen
# =====================================

def row_to_text(title, description, row):
    """
    Mengubah satu baris dataset menjadi dokumen teks.
    """

    lines = []

    # Nama dataset
    lines.append(f"Dataset : {title}")

    # Deskripsi
    if description:
        lines.append(f"Deskripsi : {description}")

    # Isi data
    for key, value in row.items():

        # Skip field yang tidak diperlukan
        if key in IGNORE_FIELDS:
            continue

        # Skip jika None
        if value is None:
            continue

        # Skip string kosong
        if str(value).strip() == "":
            continue

        lines.append(
            f"{clean_key(key)} : {value}"
        )

    return "\n".join(lines)


# =====================================
# Mengubah seluruh dataset menjadi list dokumen
# =====================================

def convert_to_documents(title, description, api_response):
    """
    Mengubah seluruh rows menjadi list dokumen.
    """

    documents = []

    rows = api_response.get("data", {}).get("rows", [])

    if len(rows) == 0:
        return documents

    for row in rows:

        document = row_to_text(
            title,
            description,
            row
        )

        documents.append(document)

    return documents