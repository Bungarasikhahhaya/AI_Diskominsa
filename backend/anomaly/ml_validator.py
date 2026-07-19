import pandas as pd

class MLValidator:

    def __init__(self, dataframe):
        self.df = dataframe

    def validate(self):
        report = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        # ==========================================
        # Check empty dataset
        # ==========================================

        if self.df.empty:
            report["valid"] = False
            report["errors"].append(
                "Dataset kosong."
            )
            return report

        # ==========================================
        # Check minimum rows
        # ==========================================

        if len(self.df) < 10:
            report["valid"] = False
            report["errors"].append(
                f"Jumlah data hanya {len(self.df)}. Minimal 10 data."
            )

        # ==========================================
        # Check feature count
        # ==========================================

        if self.df.shape[1] == 0:
            report["valid"] = False
            report["errors"].append(
                "Tidak ditemukan feature numerik."
            )

        # ==========================================
        # Check missing values
        # ==========================================

        missing = int(self.df.isnull().sum().sum())
        if missing > 0:
            report["warnings"].append(
                f"Terdapat {missing} missing value."
            )

        # ==========================================
        # Check constant feature
        # ==========================================

        constant_columns = []

        for col in self.df.columns:
            if self.df[col].nunique() <= 1:
                constant_columns.append(col)

        if constant_columns:
            report["warnings"].append(
                "Feature konstan: "
                + ", ".join(constant_columns)
            )

        # ==========================================
        # Check duplicate rows
        # ==========================================

        duplicate = int(self.df.duplicated().sum())
        if duplicate > 0:
            report["warnings"].append(
                f"Terdapat {duplicate} data duplikat."
            )

        return report