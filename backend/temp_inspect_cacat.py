import os
import pandas as pd
path = os.path.join('data', 'csv', '_Jumlah_Penderita_Cacat_Menurut_Kabupaten_Kota_di_Provinsi_Aceh.csv')
print('path', path)
df = pd.read_csv(path, nrows=20)
print('columns', df.columns.tolist())
print('sample rows')
for row in df.head(10).to_dict(orient='records'):
    print(row)
for col in df.columns:
    if any(k in col.lower() for k in ['tahun', 'year', 'periode', 'kabupaten', 'kota', 'provinsi']):
        print('col', col)
        print(df[col].dropna().unique()[:20])
