from sklearn.ensemble import IsolationForest

class AnomalyEngine:
    def __init__(
        self,
        contamination="auto",
        random_state=42
    ):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state
        )

    def detect(self, dataframe):
        result = dataframe.copy()
        prediction = self.model.fit_predict(
            dataframe
        )

        score = self.model.decision_function(
            dataframe
        )

        result["anomaly"] = prediction
        result["score"] = score

        # ======================================
        # Status
        # ======================================

        result["status"] = result["anomaly"].map({
            1: "Normal",
            -1: "Anomali"
        })

        # ======================================
        # Severity
        # ======================================

        def severity(value):
            if value >= 0:
                return "-"
            elif value > -0.05:
                return "Rendah"
            elif value > -0.15:
                return "Sedang"
            else:
                return "Tinggi"
        result["severity"] = result["score"].apply(
            severity
        )

        anomaly_count = int(
            (prediction == -1).sum()
        )

        normal_count = int(
            (prediction == 1).sum()
        )

        report = {
            "algorithm": "Isolation Forest",
            "feature_count": dataframe.shape[1],
            "total_rows": len(result),
            "anomaly_count": anomaly_count,
            "normal_count": normal_count,
            "anomaly_percentage": round(
                anomaly_count /
                len(result) * 100,
                2
            ),
            "contamination": self.model.contamination
        }

        return {
            "result_df": result,
            "report": report
        }