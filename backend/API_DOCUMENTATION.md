# Anomaly AI API

## GET /ai/datasets
Mengambil daftar dataset.

## GET /ai/report/{dataset_id}
Menampilkan informasi dataset dan kelayakan ML.

## POST /ai/analyze
Body:
{
  "dataset_id":"..."
}

Return:
dataset
summary
report
insight
recommendation
anomaly

## GET /ai/anomaly/{dataset_id}
Mengambil daftar data anomali.

Optional:
severity=Tinggi
severity=Sedang
severity=Rendah

## POST /ai/export/{dataset_id}
Menghasilkan file CSV hasil analisis.
