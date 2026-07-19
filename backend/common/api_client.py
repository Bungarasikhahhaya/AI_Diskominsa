import requests
import pandas as pd

BASE_URL = "https://satudata.acehprov.go.id/api/datasets"


class APIClient:

    def get_raw(self, dataset_id, tahun=2025):
        url = (
            f"{BASE_URL}/{dataset_id}/datasources/json"
            f"?tahun={tahun}&limit=500&page=0"
        )
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_dataset(self, dataset_id, tahun=2025):
        raw = self.get_raw(dataset_id, tahun)
        rows = raw["data"]["rows"]
        return pd.DataFrame(rows)

    def get_metadata(self, dataset_id, tahun=2025):
        raw = self.get_raw(dataset_id, tahun)
        return raw.get("metadata", {})
    
    def get_available_years(self, dataset_id):
        raw = self.get_raw(dataset_id)
        metadata = raw.get("metadata", {})
        years = metadata.get("years", [])
        return [int(item["year"]) for item in years]