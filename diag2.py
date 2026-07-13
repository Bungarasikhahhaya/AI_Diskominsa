import os
import pandas as pd
from services import data_facts

files = [
    'persentase_penduduk_yang_memiliki_akta_kelahiran_menurut_kabupaten_kota_di_Provinsi_Aceh.csv',
    'Jumlah_Penduduk_Berdasarkan_Disabilitas_dan_Usia_Sekolah_menurut_kabupaten_kota_Provinsi_Aceh.csv',
    'jumlah_penduduk_menurut_kategori_usia_berdasarkan_kabupaten_kota_.csv',
    'jumlah_penduduk_menurut_usia_sekolah.csv',
    'Jumlah_Penduduk_Usia_Kerja.csv'
]
for fname in files:
    path = os.path.join(data_facts.CSV_DIR, fname)
    print('PATH:', path)
    if not os.path.exists(path):
        print('  missing file')
        continue
    try:
        df = pd.read_csv(path, nrows=5, low_memory=False)
        print('  cols:', list(df.columns))
        print(df.head(5).to_string(index=False))
    except Exception as e:
        print('  read error', e)
    print('---')
