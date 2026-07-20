import argparse
import os
from pathlib import Path

import pandas as pd

DEFAULT_KEYWORDS = [
    'tahun', 'year', 'periode',
    'kabupaten', 'kota', 'provinsi',
    'desa', 'kecamatan', 'nama',
    'jumlah', 'nilai', 'persen', 'persentase',
    'kategori', 'kelompok', 'satuan'
]


def discover_csv_files(base_dir: Path):
    return sorted(base_dir.glob('*.csv'))


def find_matching_columns(columns, keywords):
    lowered = [col.lower() for col in columns]
    matched = []
    for col in columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in keywords):
            matched.append(col)
    return matched


def inspect_file(path: Path, keywords, sample_rows=5):
    print(f'\n=== {path.name} ===')
    print(f'path: {path}')

    try:
        df = pd.read_csv(path, nrows=20)
    except Exception as exc:
        print(f'Gagal membaca file: {exc}')
        return

    print(f'baris terdeteksi: {len(df)}')
    print('kolom:', df.columns.tolist())

    matched_cols = find_matching_columns(df.columns, keywords)
    if matched_cols:
        print('kolom relevan:')
        for col in matched_cols:
            values = df[col].dropna().astype(str).unique()[:10]
            print(f' - {col}: {list(values)}')
    else:
        print('tidak ada kolom yang cocok dengan kata kunci')

    print('contoh baris:')
    for row in df.head(sample_rows).to_dict(orient='records'):
        print(row)


def main():
    parser = argparse.ArgumentParser(description='Inspeksi cepat semua dataset CSV di folder data/csv')
    parser.add_argument('--keyword', nargs='*', default=None, help='kata kunci untuk mencari kolom yang relevan')
    parser.add_argument('--sample', type=int, default=5, help='jumlah contoh baris yang ditampilkan per file')
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent / 'data' / 'csv'
    if not base_dir.exists():
        print(f'folder tidak ditemukan: {base_dir}')
        return

    csv_files = discover_csv_files(base_dir)
    if not csv_files:
        print('tidak ada file CSV yang ditemukan')
        return

    keywords = args.keyword or DEFAULT_KEYWORDS
    print(f'ditemukan {len(csv_files)} file CSV')

    for path in csv_files:
        inspect_file(path, keywords, sample_rows=args.sample)


if __name__ == '__main__':
    main()
