import pandas as pd
from datetime import datetime
from anomaly.anomaly_service import AnomalyService


class DatasetTester:

    def __init__(self):

        self.service = AnomalyService()

    def test(self, dataset_id, year):

        try:

            result = self.service.analyze(
                dataset_id,
                year
            )
            print(year)
            print(result)

            if not result["success"]:

                return {
                    "success": False,
                    "dataset_id": dataset_id,
                    "year": year,
                    "rows": 0,
                    "columns": 0,
                    "ready_ml": False,
                    "errors": ["Analisis gagal"],
                    "warnings": []

                }

            data = result["data"]
            summary = data["summary"]

            return {
                "success": True,
                "dataset_id": dataset_id,
                "year": year,
                "rows": summary["rows"],
                "columns": summary["columns"],
                "ready_ml": summary["validation"],
                "errors": [],
                "warnings": []

            }
        except Exception as e:

            return {
                "success": False,
                "dataset_id": dataset_id,
                "year": year,
                "rows": 0,
                "columns": 0,
                "ready_ml": False,
                "errors": [str(e)],
                "warnings": []
            }

    def batch_test(self, dataframe, year, limit=20):

        results = []

        for _, row in dataframe.head(limit).iterrows():

            dataset_id = row["identifier"]
            title = row["title"]
            publisher = row["publisher"]

            result = self.auto_test(dataset_id)

            result["title"] = title
            result["publisher"] = publisher

            results.append(result)

        df = pd.DataFrame(results)

        df = df.sort_values(
            by=["ready_ml", "rows"],
            ascending=False
        )

        return df.reset_index(drop=True)

    def auto_test(self, dataset_id):

        years = self.service.client.get_available_years(dataset_id)

        if not years:
            return {
                "success": False,
                "dataset_id": dataset_id,
                "rows": 0,
                "columns": 0,
                "ready_ml": False,
                "errors": [
                    "Dataset tidak memiliki metadata tahun."
                ],
                "warnings": []
            }

        years.sort(reverse=True)

        best_result = None

        for year in years:

            result = self.test(
                dataset_id,
                year
            )

            if result["rows"] == 0:
                continue

            if best_result is None:
                best_result = result

            if result["ready_ml"]:
                return result

        if best_result is not None:
            return best_result

        return {
            "success": False,
            "dataset_id": dataset_id,
            "rows": 0,
            "columns": 0,
            "ready_ml": False,
            "errors": [
                "Dataset memiliki metadata tahun tetapi tidak dapat dianalisis."
            ],
            "warnings": []
        }