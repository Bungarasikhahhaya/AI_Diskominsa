import pandas as pd


class StatisticsEngine:

    def __init__(self, dataframe, schema):
        self.df = dataframe
        self.schema = schema

    def analyze(self):
        result = {
            "dataset": {},
            "schema": {},
            "indicators": {}
        }

        # ==========================
        # DATASET SUMMARY
        # ==========================

        missing_columns = (
            self.df.isnull()
            .sum()
            .loc[lambda x: x > 0]
            .to_dict()
        )

        result["dataset"] = {
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "duplicate_rows": int(self.df.duplicated().sum()),
            "missing_summary": {
                "total": int(
                    self.df.isnull().sum().sum()
                ),
                "columns": {
                    k: int(v)
                    for k, v in missing_columns.items()
                }
            }
        }

        # ==========================
        # SCHEMA
        # ==========================

        result["schema"] = {
            "data_types": {
                column: str(dtype)
                for column, dtype in self.df.dtypes.items()
            },
            "unique_values": {
                column: int(
                    self.df[column].nunique(dropna=True)
                )
                for column in self.df.columns
            }
        }

        # ==========================
        # INDICATOR STATISTICS
        # ==========================

        for column in self.schema["indicator"]:
            series = self.df[column].dropna()
            std = series.std()
            var = series.var()
            if pd.isna(std):
                std = 0
            if pd.isna(var):
                var = 0

            result["indicators"][column] = {
                "count": int(series.count()),
                "mean": float(series.mean()),
                "median": float(series.median()),
                "std": float(std),
                "variance": float(var),
                "min": float(series.min()),
                "max": float(series.max()),
                "q1": float(series.quantile(0.25)),
                "q3": float(series.quantile(0.75))
            }

        return result