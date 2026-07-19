import pandas as pd


class PreprocessingEngine:

    def __init__(self, dataframe, schema):
        self.original_df = dataframe.copy()
        self.schema = schema

    def process(self):
        display_df = self.original_df.copy()
        report = {
            "removed_columns": [],
            "converted_columns": [],
            "filled_missing": [],
            "remaining_missing": 0,
            "ready_for_ml": False,
            "reason": ""
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
            c
            for c in drop_columns
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

        # ==========================================
        # Ready for ML
        # ==========================================

        indicator_count = len(self.schema["indicator"])

        if len(display_df) >= 10 and indicator_count >= 1:
            report["ready_for_ml"] = True
            report["reason"] = "Dataset memenuhi syarat."
        else:
            report["reason"] = (
                "Dataset belum memenuhi syarat untuk Machine Learning."
            )

        return {
            "display_df": display_df,
            "report": report
        }