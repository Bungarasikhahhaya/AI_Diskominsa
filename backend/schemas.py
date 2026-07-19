from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    dataset_id: str

class ExportRequest(BaseModel):
    dataset_id: str
    format: str = "csv"