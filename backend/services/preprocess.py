import pandas as pd

class AnomalyPreprocessingEngine:
    def __init__(self, dataframe, schema):
        self.original_df = dataframe.copy()
        self.schema = schema

    def process(self):
        display_df = self.original_df.copy()
        report = {
            "removed_columns": [],
            "converted_columns": [],
            "filled_missing": [],
            "remaining_missing": 0
        }

        # ==========================================
        # Drop identifier, metadata, system
        # ==========================================
        drop_columns = (
            self.schema["identifier"]
            + self.schema["metadata"]
            + self.schema["system"]
        )
        existing = [
            c for c in drop_columns
            if c in display_df.columns
        ]
        display_df.drop(
            columns=existing,
            inplace=True
        )
        report["removed_columns"] = existing

        # ==========================================
        # Convert numeric indicator
        # ==========================================
        for col in self.schema["indicator"]:
            if col not in display_df.columns:
                continue
            before = str(display_df[col].dtype)
            display_df[col] = pd.to_numeric(
                display_df[col],
                errors="coerce"
            )
            after = str(display_df[col].dtype)
            if before != after:
                report["converted_columns"].append({
                    "column": col,
                    "from": before,
                    "to": after
                })

        # ==========================================
        # Missing Value
        # ==========================================
        for col in self.schema["indicator"]:
            if col not in display_df.columns:
                continue
            missing = int(display_df[col].isnull().sum())
            if missing > 0:
                median = display_df[col].median()
                display_df[col] = display_df[col].fillna(
                    median
                )
                report["filled_missing"].append({
                    "column": col,
                    "count": missing,
                    "method": "median"
                })
        report["remaining_missing"] = int(
            display_df.isnull().sum().sum()
        )

        return {
            "display_df": display_df,
            "report": report
        }
    
    def build_features(self, dataframe):

        indicator_columns = [
            col
            for col in self.schema["indicator"]
            if col in dataframe.columns
        ]

        ml_df = dataframe[indicator_columns].copy()

        report = {
            "feature_count": len(indicator_columns),
            "features": indicator_columns,
            "main_indicator": (
                indicator_columns[0]
                if indicator_columns
                else None
            ),
            "shape": ml_df.shape
        }

        return {
            "ml_df": ml_df,
            "report": report
        }
    
    def validate(self, dataframe):

        report = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        if dataframe.empty:
            report["valid"] = False
            report["errors"].append(
                "Dataset kosong."
            )
            return report

        if len(dataframe) < 10:
            report["valid"] = False
            report["errors"].append(
                f"Jumlah data hanya {len(dataframe)}. Minimal 10 data."
            )

        if dataframe.shape[1] == 0:
            report["valid"] = False
            report["errors"].append(
                "Tidak ditemukan feature numerik."
            )

        missing = int(
            dataframe.isnull().sum().sum()
        )

        if missing > 0:
            report["warnings"].append(
                f"Terdapat {missing} missing value."
            )

        constant_columns = []

        for col in dataframe.columns:
            if dataframe[col].nunique() <= 1:
                constant_columns.append(col)

        if constant_columns:
            report["warnings"].append(
                "Feature konstan: "
                + ", ".join(constant_columns)
            )

        duplicate = int(
            dataframe.duplicated().sum()
        )

        if duplicate > 0:
            report["warnings"].append(
                f"Terdapat {duplicate} data duplikat."
            )

        return report

