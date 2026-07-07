def row_to_text(title, description, row):
    """
    Mengubah satu baris data menjadi dokumen teks.
    """

    text = f"Dataset : {title}\n\n"

    if description:
        text += f"Deskripsi : {description}\n\n"

    for key, value in row.items():

        if value is not None:
            text += f"{key} : {value}\n"

    return text.strip()


def convert_to_documents(title, description, api_response):
    """
    Mengubah seluruh rows menjadi list dokumen.
    """

    documents = []

    rows = api_response["data"]["rows"]

    for row in rows:

        documents.append(
            row_to_text(
                title,
                description,
                row
            )
        )

    return documents