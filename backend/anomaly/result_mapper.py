import pandas as pd

class ResultMapper:

    def map(
        self,
        display_df,
        anomaly_df,
        indicator
    ):
        result = display_df.copy()
        result.insert(0, "row_number", range(1, len(result) + 1))
        result["anomaly"] = anomaly_df["anomaly"].values
        result["status"] = anomaly_df["status"].values
        result["severity"] = anomaly_df["severity"].values
        result["score"] = (anomaly_df["score"].abs().round(3))
        result["indicator"] = indicator
        result["indicator_value"] = result[indicator]
        return result