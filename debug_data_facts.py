import sys
from pathlib import Path
repo = Path(r'D:\BUNGA\DISKOMINSA')
sys.path.insert(0, str(repo))
from services import data_facts, query_parser

questions = [
    'kabupaten mana yang memilik persentase penduduk terbanyak yang sudah memiliki akta kelahiran pada provinsi aceh?',
    'berapa jumlah penduduk dengan usia SD pada kabupaten simeulue?'
]
for q in questions:
    print('\nQUESTION:', q)
    parsed = query_parser.parse_question(q)
    print('parsed:', parsed)
    q_tokens = data_facts._tokens(q)
    print('tokens:', q_tokens)
    metric_token = data_facts._find_metric_token(q_tokens)
    print('metric_token:', metric_token)
    file_index = data_facts._build_file_index()
    scored = []
    for meta in file_index:
        score = data_facts._score_file_for_question(meta, q_tokens, metric_token, q)
        if score > 0:
            scored.append((score, meta['name']))
    scored.sort(reverse=True)
    print('TOP 20:')
    for s, name in scored[:20]:
        print(f'{s:3} {name}')
    for meta in file_index:
        if meta['name'] in {
            'persentase_penduduk_yang_memiliki_akta_kelahiran_menurut_kabupaten_kota_di_provinsi_aceh.csv',
            'jumlah_penduduk_berdasarkan_disabilitas_dan_usia_sekolah_menurut_kabupaten_kota_provinsi_aceh.csv',
            'jumlah_penduduk_menurut_kategori_usia_berdasarkan_kabupaten_kota_.csv',
            'jumlah_penduduk_menurut_usia_sekolah.csv'
        }:
            print('SPECIFIC', meta['name'], data_facts._score_file_for_question(meta, q_tokens, metric_token, q))
    ans, src = data_facts.answer(q, parsed.get('region'), parsed.get('year'))
    print('answer:', ans)
    print('source:', src)

# Inspect critical dataset row selection for SD query.
print('\nINSPECT SD DATASET')
path = data_facts.CSV_DIR + r'\\Jumlah_Penduduk_Berdasarkan_Disabilitas_dan_Usia_Sekolah_menurut_kabupaten_kota_Provinsi_Aceh.csv'
import pandas as pd
df = pd.read_csv(path, low_memory=False)
print('Columns:', list(df.columns))
# Filter rows for Simeulue and SD
mask = df['bps_nama_kabupaten_kota'].str.contains('Simeulue', case=False, na=False) & df['usia_sekolah'].astype(str).str.lower().str.contains('sd|sederajat')
filtered = df[mask]
print('Filtered rows count:', len(filtered))
print(filtered[['tahun','semester','jenis_kelamin','jenis_disabilitas','usia_sekolah','jumlah_penduduk']].head(20).to_string(index=False))
