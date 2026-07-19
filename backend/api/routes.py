from fastapi import APIRouter
from common.dataset_discovery import DatasetDiscovery
from common.dataset_tester import DatasetTester
from schemas import AnalyzeRequest
from anomaly.anomaly_service import AnomalyService
from api.response import APIResponse
from export.export_service import ExportService
from typing import Optional
import pandas as pd

router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)

@router.get("/datasets")
def get_datasets(

    publisher: Optional[str] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):

    try:
        discovery = DatasetDiscovery()
        df = discovery.simplify()

        # ==========================
        # Filter Publisher
        # ==========================

        if publisher:
            df = df[
                df["publisher"]
                .str.contains(
                    publisher,
                    case=False,
                    na=False
                )
            ]

        # ==========================
        # Filter Category
        # ==========================

        if category:
            df = df[
                df["category"]
                .str.contains(
                    category,
                    case=False,
                    na=False
                )
            ]

        # ==========================
        # Filter Keyword
        # ==========================

        if keyword:
            keyword = keyword.strip()
            df = df[
                df["title"]
                .str.contains(
                    keyword,
                    case=False,
                    na=False
                )
            ]

        # ==========================
        # Pagination
        # ==========================

        total = len(df)
        start = (page - 1) * limit
        end = start + limit
        items = df.iloc[start:end]
        return APIResponse.success(
            {
                "total": total,
                "page": page,
                "limit": limit,
                "items": items.to_dict(
                    orient="records"
                )
            },
            "Dataset berhasil dimuat"
        )

    except Exception as e:
        return APIResponse.error(
            str(e)
        )


@router.get("/report/{dataset_id}")

def dataset_report(dataset_id: str):
    try:
        tester = DatasetTester()
        result = tester.auto_test(dataset_id)
        return APIResponse.success(
            result,
            "Report berhasil dibuat"
        )
    except Exception as e:
        return APIResponse.error(
            str(e)
        )
    
@router.post("/analyze")
def analyze(request: AnalyzeRequest):

    try:
        service = AnomalyService()
        years = service.client.get_available_years(
            request.dataset_id
        )

        if not years:
            return APIResponse.error(
                "Dataset tidak memiliki metadata tahun."
            )

        year = max(years)
        result = service.analyze(
            request.dataset_id,
            year
        )

        if not result["success"]:
            return APIResponse.error(
                "Dataset belum layak untuk Machine Learning."
            )

        return APIResponse.success(
            result["data"],
            "Analisis selesai."
        )

    except Exception as e:
        return APIResponse.error(
            str(e)
        )

@router.post("/export/{dataset_id}")
def export_result(dataset_id: str):

    try:

        # Cari tahun dataset yang valid
        tester = DatasetTester()
        dataset = tester.auto_test(dataset_id)
        if not dataset["ready_ml"]:
            return APIResponse.error(
                "Dataset tidak layak untuk Machine Learning."
            )

        # Jalankan analisis
        service = AnomalyService()
        result = service.analyze(
            dataset_id,
            dataset["year"]
        )

        # Ambil hanya data anomali
        dataframe = pd.DataFrame(
            result["data"]["anomaly"]["all"]
        )

        # Export ke CSV
        exporter = ExportService()
        path = exporter.export_csv(
            dataframe,
            f"anomaly_{dataset_id}"
        )

        return APIResponse.success(
            {
                "file": path
            },
            "Export berhasil."
        )

    except Exception as e:
        return APIResponse.error(
            str(e)
        )

@router.get("/anomaly/{dataset_id}")

def get_anomaly(
    dataset_id: str,
    severity: Optional[str] = None
):

    try:

        tester = DatasetTester()
        dataset = tester.auto_test(
            dataset_id
        )

        if not dataset["ready_ml"]:
            return APIResponse.error(
                "Dataset belum layak ML."
            )

        service = AnomalyService()
        result = service.analyze(
            dataset_id,
            dataset["year"]
        )

        df = pd.DataFrame(
            result["data"]["anomaly"]["all"]
        )

        if severity:
            anomaly = df[
                df["severity"].str.lower() == severity.lower()
            ]
        else:
            anomaly = df

        return APIResponse.success(
            {
                "count": len(anomaly),
                "rows":
                    anomaly.to_dict(
                        orient="records"
                    )
            },
            "Data berhasil diambil"
        )

    except Exception as e:

        return APIResponse.error(
            str(e)
        )