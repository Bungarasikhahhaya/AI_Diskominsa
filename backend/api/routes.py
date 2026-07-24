from typing import Optional

import pandas as pd
from fastapi import APIRouter

from api.response import APIResponse
from common.dataset_discovery import DatasetDiscovery
from schemas import AnalyzeRequest
from services.anomaly import AnomalyService

router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)

service = AnomalyService()


@router.get("/datasets")
def get_datasets(
    publisher: Optional[str] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    try:
        df = DatasetDiscovery().simplify()

        if publisher:
            df = df[
                df["publisher"].str.contains(
                    publisher,
                    case=False,
                    na=False
                )
            ]

        if category:
            df = df[
                df["category"].str.contains(
                    category,
                    case=False,
                    na=False
                )
            ]

        if keyword:
            df = df[
                df["title"].str.contains(
                    keyword.strip(),
                    case=False,
                    na=False
                )
            ]

        total = len(df)
        start = (page - 1) * limit
        end = start + limit

        return APIResponse.success(
            {
                "total": total,
                "page": page,
                "limit": limit,
                "items": df.iloc[start:end].to_dict(
                    orient="records"
                )
            },
            "Dataset berhasil dimuat"
        )

    except Exception as e:
        return APIResponse.error(str(e))


@router.post("/analyze")
def analyze(request: AnalyzeRequest):

    try:
        years = service.client.get_available_years(
            request.dataset_id
        )

        if not years:
            return APIResponse.error(
                "Dataset tidak memiliki metadata tahun."
            )

        result = service.analyze(
            request.dataset_id,
            max(years)
        )

        if not result["success"]:
            return APIResponse.error(
                "Dataset belum layak untuk Machine Learning.",
                {
                    "validation": result["validation"],
                    "statistics": result["statistics"]
                }
            )

        return APIResponse.success(
            result["data"],
            "Analisis selesai."
        )

    except Exception as e:
        return APIResponse.error(str(e))


@router.get("/anomaly/{dataset_id}")
def get_anomaly(
    dataset_id: str,
    severity: Optional[str] = None
):

    try:
        years = service.client.get_available_years(
            dataset_id
        )

        if not years:
            return APIResponse.error(
                "Dataset tidak memiliki metadata tahun."
            )

        result = service.analyze(
            dataset_id,
            max(years)
        )

        if not result["success"]:
            return APIResponse.error(
                "Dataset belum layak untuk Machine Learning."
            )

        df = pd.DataFrame(
            result["data"]["anomaly"]["all"]
        )

        if severity:
            df = df[
                df["severity"].str.lower() == severity.lower()
            ]

        return APIResponse.success(
            {
                "count": len(df),
                "rows": df.to_dict(
                    orient="records"
                )
            },
            "Data berhasil diambil"
        )

    except Exception as e:
        return APIResponse.error(str(e))