from common.api_client import APIClient
from anomaly.schema_analyzer import DataProfiler
from anomaly.statistics_engine import StatisticsEngine
from anomaly.preprocessing import PreprocessingEngine
from anomaly.feature_builder import FeatureBuilder
from anomaly.ml_validator import MLValidator
from anomaly.anomaly_engine import AnomalyEngine
from anomaly.result_mapper import ResultMapper
from anomaly.recommendation_generator import RecommendationGenerator
from anomaly.response_builder import ResponseBuilder
from anomaly.report_generator import ReportGenerator
from anomaly.response_builder import ResponseBuilder
from anomaly.insight_generator import InsightGenerator
from common.dataset_discovery import DatasetDiscovery

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

        metadata = self.client.get_metadata(
            dataset_id,
            year
        )

        dataset_meta = DatasetDiscovery().get_dataset_info(
            dataset_id
        )

        # ==========================================
        # Schema Analyzer
        # ==========================================

        schema = DataProfiler(df).profile()

        # ==========================================
        # Statistics
        # ==========================================

        statistics = StatisticsEngine(
            df,
            schema
        ).analyze()

        # ==========================================
        # Preprocessing
        # ==========================================

        preprocessing = PreprocessingEngine(
            df,
            schema
        ).process()

        display_df = preprocessing["display_df"]

        # ==========================================
        # Feature Builder
        # ==========================================

        feature = FeatureBuilder(
            display_df,
            schema
        ).build()

        ml_df = feature["ml_df"]

        # ==========================================
        # Validator
        # ==========================================

        validation = MLValidator(
            ml_df
        ).validate()

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

        anomaly = AnomalyEngine().detect(
            ml_df
        )

        # ==========================================
        # Map Result
        # ==========================================

        mapped_result = ResultMapper().map(
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

        report = ReportGenerator(
            mapped_result
        ).build()

        # ==========================================
        # Insight
        # ==========================================

        insight = InsightGenerator(
            mapped_result,
            anomaly["report"]
        ).build()

        # ==========================================
        # Recommendation
        # ==========================================

        recommendation = RecommendationGenerator(
            mapped_result,
            report
        ).build()

        # ==========================================
        # Response
        # ==========================================
                
        response = ResponseBuilder(
            dataset_info,
            schema,
            statistics,
            validation,
            anomaly,
            mapped_result,
            report,
            insight,
            recommendation
        ).build()

        return {
            "success": True,
            "data": response
        }