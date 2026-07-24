import pandas as pd
import requests
from rapidfuzz import process

class DatasetDiscovery:
    def __init__(self):
        self.catalog_url = (
            "https://satudata.acehprov.go.id/data.json"
        )

    def get_catalog(self):
        response = requests.get(self.catalog_url)
        response.raise_for_status()
        return response.json()

    def simplify(self):
        catalog = self.get_catalog()
        datasets = catalog["dataset"]
        result = []
        for item in datasets:
            publisher = item.get("publisher", {})
            result.append({
                "identifier": item.get("identifier"),
                "title": item.get("title"),
                "publisher": publisher.get("name"),
                "issued": item.get("issued"),
                "modified": item.get("modified"),
                "landing_page": item.get("landingPage")
            })

        return pd.DataFrame(result)
    
    def summary(self):
        df = self.simplify()
        return {
            "total_dataset": len(df),
            "total_instansi": df["publisher"].nunique(),
            "top_publishers": (
                df["publisher"]
                .value_counts()
                .head(10)
                .to_dict()
            ),

            "top_categories": (
                df["kategori"]
                .fillna("Unknown")
                .value_counts()
                .head(10)
                .to_dict()
            )
        }
    
    def find_candidates(
        self,
        publisher=None,
        kategori=None,
        keyword=None
    ):

        df = self.simplify()
        if publisher:
            df = df[
                df["publisher"]
                .str.contains(
                    publisher,
                    case=False,
                    na=False
                )
            ]

        if kategori:
            df = df[
                df["kategori"]
                .str.contains(
                    kategori,
                    case=False,
                    na=False
                )
            ]

        if keyword:
            titles = df["title"].fillna("").tolist()
            matches = process.extract(
                keyword,
                titles,
                limit=20,
                score_cutoff=40
            )
            matched_titles = [
                match[0]
                for match in matches
            ]
            df = df[
                df["title"].isin(
                    matched_titles
                )
            ]

        return df.reset_index(drop=True)
    
    def get_dataset_info(self, dataset_id):
        catalog = self.get_catalog()
        for item in catalog["dataset"]:
            if item.get("identifier") == dataset_id:
                publisher = item.get("publisher", {})

                return {
                    "title": item.get("title"),
                    "publisher": publisher.get("name"),
                    "issued": item.get("issued"),
                    "modified": item.get("modified")
                }

        return {}