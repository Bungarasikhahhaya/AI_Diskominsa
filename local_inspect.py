import os
import pandas as pd

def main():
    from services import data_facts

    base = data_facts.CSV_DIR

    candidates = [
        'persentase_penduduk_yang_memiliki_akta_kelahiran_menurut_kabupaten_kota_di_Provinsi_Aceh.csv',
        'jumlah_penduduk_berdasarkan_disabilitas_dan_usia_sekolah_menurut_kabupaten_kota_provinsi_aceh.csv',
        'jumlah_penduduk_menurut_kelompok_umur_kabupaten_kota.csv',
        'jumlah_penduduk_menurut_usia_muda__usia_produktif_dan_usia_tua_provinsi_aceh.csv'
    ]
    for fname in candidates:
        path = os.path.join(base, fname)
        print('PATH:', path)
        if not os.path.exists(path):
            print('  missing file')
            continue
        df = pd.read_csv(path, nrows=8, low_memory=False)
        print('  cols:', list(df.columns))
        print(df.head(5).to_string(index=False))
        print('---')

if __name__ == '__main__':
    main()
