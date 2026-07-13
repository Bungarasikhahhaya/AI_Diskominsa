import requests

CATALOG_URL = "https://satudata.acehprov.go.id/data.json"

def get_catalog():
    """
    Mengambil seluruh daftar dataset dari Satu Data Aceh.
    """

    response = requests.get(CATALOG_URL, timeout=30)
    response.raise_for_status()

    data = response.json()

    return data.get("dataset", [])