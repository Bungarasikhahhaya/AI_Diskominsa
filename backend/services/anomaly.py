from common.api_client import APIClient
from common.dataset_discovery import DatasetDiscovery
from sklearn.ensemble import IsolationForest
from services.preprocess import AnomalyPreprocessingEngine
from services.postprocess import PostprocessEngine
from services.profile import ProfileEngine

class AnomalyService:

    def __init__(self):
        self.client = APIClient()
        
    def analyze(self, dataset_id, year):

        # ==========================================
        # Load Dataset
        # ==========================================

        df = self.client.get_dataset(
            dataset_id,
            year
        )

        dataset_meta = DatasetDiscovery().get_dataset_info(
            dataset_id
        )

        # ==========================================
        # Profiling 
        # ==========================================
        profiler = ProfileEngine(df)
        schema = profiler.profile()
        statistics = profiler.analyze(
            df,
            schema
        )

        # ==========================================
        # Preprocessing
        # ==========================================

        preprocessor = AnomalyPreprocessingEngine(
            df,
            schema
        )

        preprocessing = preprocessor.process()
        display_df = preprocessing["display_df"]
        feature = preprocessor.build_features(
            display_df
        )
        ml_df = feature["ml_df"]
        validation = preprocessor.validate(
            ml_df
        )

        # ==========================================
        # Stop if invalid
        # ==========================================

        if not validation["valid"]:
            return {
                "success": False,
                "schema": schema,
                "statistics": statistics,
                "preprocessing": preprocessing["report"],
                "feature_builder": feature["report"],
                "validation": validation,
                "anomaly": None
            }

        # ==========================================
        # Run ML
        # ==========================================

        anomaly = self.detect(
            ml_df
        )
        postprocess = PostprocessEngine()

        # ==========================================
        # Map Result
        # ==========================================

        mapped_result = postprocess.map_result(
            display_df,
            anomaly["result_df"],
            feature["report"]["main_indicator"]
        )

        dataset_info = {
            "id": dataset_id,
            "title": dataset_meta.get("title"),
            "publisher": dataset_meta.get("publisher"),
            "year": year,
            "issued": dataset_meta.get("issued"),
            "modified": dataset_meta.get("modified"),
            "rows": len(df),
            "columns": len(df.columns)
        }

        # ==========================================
        # Report
        # ==========================================

        report = self.build_report(
            mapped_result
        )

        # ==========================================
        # Insight
        # ==========================================

        insight = postprocess.build_insight(
            mapped_result,
            anomaly["report"]
        )

        # ==========================================
        # Recommendation
        # ==========================================

        recommendation = postprocess.build_recommendation(
            mapped_result,
            report
        )

        # ==========================================
        # Response
        # ==========================================
                
        response = postprocess.build_response(
            dataset_info,
            statistics,
            validation,
            anomaly,
            mapped_result,
            report,
            insight,
            recommendation
        )

        return {
            "success": True,
            "data": response
        }
    
    def detect(self, dataframe):
        result = dataframe.copy()
        model = IsolationForest(
            contamination="auto",
            random_state=42
        )
        prediction = model.fit_predict(
            dataframe
        )
        score = model.decision_function(
            dataframe
        )
        result["anomaly"] = prediction
        result["score"] = score
        result["status"] = result["anomaly"].map({
            1: "Normal",
            -1: "Anomali"
        })

        # ======================================
        # Severity
        # ======================================

        result["severity"] = result["score"].apply(
            self._severity
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
                anomaly_count / len(result) * 100,
                2
            ),
            "contamination": model.contamination
        }

        return {
            "result_df": result,
            "report": report
        }

    def _severity(self, score):
        if score >= 0:
            return "-"
        if score > -0.05:
            return "Rendah"
        if score > -0.15:
            return "Sedang"
        return "Tinggi"
    
    def build_report(self, dataframe):

        anomaly = dataframe[
            dataframe["anomaly"] == -1
        ]

        return {
            "total_rows": len(dataframe),
            "anomaly_count": len(anomaly),
            "normal_count": len(dataframe) - len(anomaly),
            "anomaly_percentage": round(
                len(anomaly) / len(dataframe) * 100,
                2
            ),
            "top_anomalies": (
                anomaly
                .sort_values("score")
                .head(10)
                .to_dict(orient="records")
            )
        }
    