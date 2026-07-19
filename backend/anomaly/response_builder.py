class ResponseBuilder:

    def __init__(
        self,
        dataset_info,
        schema,
        statistics,
        validation,
        anomaly,
        mapped_result,
        report,
        insight,
        recommendation
    ):

        self.dataset_info = dataset_info
        self.schema = schema
        self.statistics = statistics
        self.validation = validation
        self.anomaly = anomaly
        self.mapped_result = mapped_result
        self.report = report
        self.insight = insight
        self.recommendation = recommendation

    def build(self):
        from datetime import datetime
        anomaly_only = self.mapped_result[
            self.mapped_result["anomaly"] == -1
        ]

        return {
            "generated_at": datetime.now().isoformat(),
            "dataset": self.dataset_info,
            "summary": {
                "rows": self.statistics["dataset"]["rows"],
                "columns": self.statistics["dataset"]["columns"],
                "validation": self.validation["valid"],
                "algorithm": self.anomaly["report"]["algorithm"],
                "anomaly_count": self.anomaly["report"]["anomaly_count"],
                "normal_count": self.anomaly["report"]["normal_count"],
                "anomaly_percentage": self.anomaly["report"]["anomaly_percentage"]
            },
            "report": self.report,
            "insight": self.insight,
            "recommendation": self.recommendation,
            "anomaly": {
                "count": len(anomaly_only),
                "top": (
                    anomaly_only
                    .sort_values(by="score")
                    .head(10)
                    .to_dict(orient="records")
                ),
                "all": self.mapped_result.to_dict(
                    orient="records"
                )
            }

        }