import pandas as pd


class FeatureBuilder:

    def __init__(self, dataframe, schema):

        self.df = dataframe
        self.schema = schema

    def build(self):

        indicator_columns = [
            col
            for col in self.schema["indicator"]
            if col in self.df.columns
        ]

        ml_df = self.df[
            indicator_columns
        ].copy()

        report = {
            "feature_count": len(indicator_columns),
            "features": indicator_columns,
            "main_indicator": indicator_columns[0] if indicator_columns else None,
            "shape": ml_df.shape
        }

        return {
            "ml_df": ml_df,
            "report": report
        }