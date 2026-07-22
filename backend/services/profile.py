import pandas as pd

METADATA_COLUMNS = {
    "satuan",
    "tingkat_penyajian",
    "kategori",
    "sumber"
}

SYSTEM_COLUMNS = {
    "created_at",
    "updated_at",
    "deleted_at"
}

def safe_float(value):
    if pd.isna(value):
        return 0.0
    return float(value)

class ProfileEngine:

    def __init__(self, dataframe):
        self.df = dataframe

    def profile(self):

        profile = {
            "identifier": [],
            "geographic": [],
            "temporal": [],
            "indicator": [],
            "metadata": [],
            "system": [],
            "others": []
        }

        for col in self.df.columns:

            name = col.lower()

            # Identifier
            if name in ["id", "uuid"]:
                profile["identifier"].append(col)

            # System Metadata
            elif name in SYSTEM_COLUMNS:
                profile["system"].append(col)

            # Metadata
            elif name in METADATA_COLUMNS:
                profile["metadata"].append(col)

            # Temporal
            elif name in [
                "tahun",
                "bulan",
                "tanggal",
                "semester",
                "triwulan"
            ]:
                profile["temporal"].append(col)

            # Geographic
            elif (
                "provinsi" in name
                or "kabupaten" in name
                or "kecamatan" in name
                or "desa" in name
                or name.startswith("bps_")
                or name.startswith("kemendagri_")
            ):
                profile["geographic"].append(col)

            # Candidate Indicator
            elif pd.api.types.is_numeric_dtype(self.df[col]):
                profile["indicator"].append(col)

            else:
                profile["others"].append(col)

        return profile

    def analyze(
        self,
        dataframe,
        schema
    ):
        result = {
            "dataset": {},
            "schema": {},
            "indicators": {}
        }

        # ==========================
        # DATASET SUMMARY
        # ==========================

        missing_columns = (
            dataframe.isnull()
            .sum()
            .loc[lambda x: x > 0]
            .to_dict()
        )

        result["dataset"] = {
            "rows": len(dataframe),
            "columns": len(dataframe.columns),
            "duplicate_rows": int(dataframe.duplicated().sum()),
            "missing_summary": {
                "total": int(
                    dataframe.isnull().sum().sum()
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
                for column, dtype in dataframe.dtypes.items()
            },
            "unique_values": {
                column: int(
                    dataframe[column].nunique(dropna=True)
                )
                for column in dataframe.columns
            }
        }

        # ==========================
        # INDICATOR STATISTICS
        # ==========================

        for column in schema["indicator"]:
            series = dataframe[column].dropna()
            std = series.std()
            if pd.isna(std):
                std = 0
            var = series.var()
            if pd.isna(var):
                var = 0

            result["indicators"][column] = {
                "count": int(series.count()),
                "mean": safe_float(series.mean()),
                "median": safe_float(series.median()),
                "std": safe_float(std),
                "variance": safe_float(var),
                "min": safe_float(series.min()),
                "max": safe_float(series.max()),
                "q1": safe_float(series.quantile(0.25)),
                "q3": safe_float(series.quantile(0.75))
            }

        return result
    
    