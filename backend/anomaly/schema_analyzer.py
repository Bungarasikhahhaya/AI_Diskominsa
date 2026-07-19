import pandas as pd


class DataProfiler:

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

        metadata_columns = [
            "satuan",
            "tingkat_penyajian",
            "kategori",
            "sumber"
        ]

        system_columns = [
            "created_at",
            "updated_at",
            "deleted_at"
        ]

        for col in self.df.columns:

            name = col.lower()

            # Identifier
            if name in ["id", "uuid"]:
                profile["identifier"].append(col)

            # System Metadata
            elif name in system_columns:
                profile["system"].append(col)

            # Metadata
            elif name in metadata_columns:
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