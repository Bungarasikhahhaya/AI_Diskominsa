import requests

BASE_URL = "https://satudata.acehprov.go.id/api/datasets"


def get_dataset(identifier, year=None, limit=500, page=0):
    """
    Mengambil data JSON berdasarkan identifier dataset.
    """

    url = f"{BASE_URL}/{identifier}/datasources/json"

    params = {
        "limit": limit,
        "page": page,
        "sortByColumn": "",
        "sortByType": ""
    }

    if year is not None:
        params["tahun"] = year

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Gagal mengambil dataset {identifier}")
        print(e)
        return None