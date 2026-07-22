class ReportGenerator:

    def __init__(self, dataframe):
        self.df = dataframe

    def build(self):
        anomaly = self.df[
            self.df["anomaly"] == -1
        ]

        return {
            "total_rows": len(self.df),
            "anomaly_count": len(anomaly),
            "normal_count": len(self.df) - len(anomaly),
            "anomaly_percentage": round(
                len(anomaly) / len(self.df) * 100,
                2
            ),
            "top_anomalies": (
                anomaly
                .sort_values("score")
                .head(10)
                .to_dict(orient="records")
            )
        }