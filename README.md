# SADA-AI — AI Deteksi Anomali Data Satu Data Aceh

Modul AI untuk mendeteksi anomali pada dataset Portal Satu Data Aceh menggunakan algoritma Machine Learning berbasis Isolation Forest.

## Deskripsi

SADA-AI merupakan salah satu modul AI yang dikembangkan dalam kegiatan Kerja Praktik (KKP) di Dinas Komunikasi, Informatika dan Persandian Aceh (Diskominsa Aceh).

Modul ini membantu administrator mengidentifikasi data yang menyimpang (anomali) sehingga proses validasi kualitas data dapat dilakukan lebih cepat sebelum dataset dipublikasikan.

---

## Fitur

- Pencarian dataset Satu Data Aceh
- Analisis otomatis menggunakan Isolation Forest
- Deteksi data anomali
- Tingkat prioritas anomali (Rendah, Sedang, Tinggi)
- Visualisasi distribusi anomali per kabupaten/kota
- Ringkasan statistik dataset
- Insight otomatis berbasis hasil AI
- Rekomendasi tindak lanjut
- Tabel data anomali dengan nomor baris dataset asli

---

## Teknologi

### Backend

- Python
- FastAPI
- Pandas
- NumPy
- Scikit-learn
- Requests

### Frontend

- React
- Vite
- Tailwind CSS
- Recharts
- Axios

---

## Struktur Proyek
backend/
├── app/
├── services/
├── engine/
├── analyzer/
└── main.py

frontend/
├── src/
├── components/
├── pages/
└── services/

---

## Cara Kerja
1. Pengguna memilih dataset.
2. Sistem mengambil data melalui API Satu Data Aceh.
3. Dataset diproses dan dibersihkan.
4. Feature numerik dipilih otomatis.
5. Isolation Forest mendeteksi data anomali.
6. AI memberikan:
* Ringkasan analisis
* Distribusi tingkat prioritas
* Insight
* Rekomendasi
7. Hasil ditampilkan dalam bentuk tabel dan visualisasi.

## Algritma
* Isolation Forest

## Output algoritma meliputi:

* Anomaly Score
* Status Data
* Tingkat Prioritas (Severity)