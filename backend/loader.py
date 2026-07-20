from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import pandas as pd

from .db import DB_PATH, HISTORICAL_DIR, PROJECTION_CSV, ensure_schema, get_connection

SUMMARY_COLUMNS = {
    'file_sumber',
    'indikator',
    'level_wilayah',
    'satuan',
    'jumlah_titik_tahun',
    'tahun_terakhir',
    'nilai_terakhir',
    'slope_per_tahun',
    'r_squared',
    'arah_tren',
    'catatan',
    'insight_text',
}
IDENTITY_WILAYAH_COLUMNS = (
    'wilayah',
    'bps_nama_desa',
    'bps_nama_kecamatan',
    'bps_nama_kabupaten_kota',
    'bps_nama_provinsi',
    'bps_nama_kab',
    'bps_nama_kota',
)
PROJECTION_YEAR_PATTERN = re.compile(r'^tahun_\+\d+$')
PROJECTION_VALUE_PATTERN = re.compile(r'^proyeksi_\+\d+$')


def read_csv_fallback(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding='utf-8-sig')


def normalize_text(value: object) -> str:
    if value is None:
        return ''
    if isinstance(value, float) and pd.isna(value):
        return ''
    text = str(value).strip()
    if text.lower() == 'nan':
        return ''
    return text


def extract_wilayah(row: pd.Series) -> str:
    for column in IDENTITY_WILAYAH_COLUMNS:
        if column in row.index:
            value = normalize_text(row[column])
            if value:
                return value
    return '-'


def extract_detail_payload(row: pd.Series, excluded_columns: set[str]) -> dict[str, str]:
    detail: dict[str, str] = {}
    for column in row.index:
        if column in excluded_columns:
            continue
        if column in IDENTITY_WILAYAH_COLUMNS:
            continue
        if PROJECTION_YEAR_PATTERN.match(column) or PROJECTION_VALUE_PATTERN.match(column):
            continue
        value = normalize_text(row[column])
        if value:
            detail[column] = value
    return detail


def to_int(value: object) -> int | None:
    text = normalize_text(value)
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def to_float(value: object) -> float | None:
    text = normalize_text(value)
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def upsert_indicator(connection: sqlite3.Connection, row: pd.Series) -> int:
    cursor = connection.execute(
        '''
        INSERT INTO indikator (nama, file_sumber, level_wilayah, satuan)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(nama) DO UPDATE SET
            file_sumber = excluded.file_sumber,
            level_wilayah = excluded.level_wilayah,
            satuan = excluded.satuan
        ''',
        (
            normalize_text(row.get('indikator')),
            normalize_text(row.get('file_sumber')),
            normalize_text(row.get('level_wilayah')),
            normalize_text(row.get('satuan')),
        ),
    )
    indicator_name = normalize_text(row.get('indikator'))
    record = connection.execute('SELECT id FROM indikator WHERE nama = ?', (indicator_name,)).fetchone()
    if record is None:
        raise RuntimeError(f'Gagal menyimpan indikator: {indicator_name}')
    return int(record['id'])


def load_historical_series(connection: sqlite3.Connection, indicator_id: int, csv_path: Path) -> int:
    dataframe = read_csv_fallback(csv_path)
    detail_rows: list[dict[str, object]] = []
    for _, row in dataframe.iterrows():
        wilayah = extract_wilayah(row)
        tahun = to_int(row.get('tahun'))
        nilai = to_float(row.get('nilai'))
        if tahun is None or nilai is None:
            continue
        detail_rows.append(
            {
                'indikator_id': indicator_id,
                'wilayah': wilayah,
                'tahun': tahun,
                'nilai': nilai,
                'detail_json': json.dumps(
                    extract_detail_payload(row, {'tahun', 'nilai', 'level_wilayah', 'satuan'}),
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            }
        )

    if not detail_rows:
        return 0

    detail_df = pd.DataFrame(detail_rows)
    connection.executemany(
        '''
        INSERT INTO historis_detail (indikator_id, wilayah, tahun, nilai, detail_json)
        VALUES (?, ?, ?, ?, ?)
        ''',
        [
            (
                row.indikator_id,
                row.wilayah,
                int(row.tahun),
                float(row.nilai),
                row.detail_json,
            )
            for row in detail_df.itertuples(index=False)
        ],
    )

    grouped = detail_df.groupby(['wilayah', 'tahun'], as_index=False)['nilai'].mean()
    connection.executemany(
        '''
        INSERT OR REPLACE INTO historis (indikator_id, wilayah, tahun, nilai)
        VALUES (?, ?, ?, ?)
        ''',
        [
            (
                indicator_id,
                row.wilayah,
                int(row.tahun),
                float(row.nilai),
            )
            for row in grouped.itertuples(index=False)
        ],
    )
    return int(len(grouped))


def load_projection_series(connection: sqlite3.Connection, indicator_id: int, rows: pd.DataFrame) -> int:
    detail_rows: list[dict[str, object]] = []

    for _, row in rows.iterrows():
        wilayah = extract_wilayah(row)
        tahun_terakhir = to_int(row.get('tahun_terakhir'))
        nilai_terakhir = to_float(row.get('nilai_terakhir'))
        slope_per_tahun = to_float(row.get('slope_per_tahun'))
        r_squared = to_float(row.get('r_squared'))
        arah_tren = normalize_text(row.get('arah_tren'))
        catatan = normalize_text(row.get('catatan'))
        insight_text = normalize_text(row.get('insight_text'))
        detail_payload = json.dumps(
            extract_detail_payload(row, SUMMARY_COLUMNS),
            ensure_ascii=False,
            sort_keys=True,
        )

        for index in range(1, 4):
            tahun_target = to_int(row.get(f'tahun_+{index}'))
            nilai_target = to_float(row.get(f'proyeksi_+{index}'))
            if tahun_target is None or nilai_target is None:
                continue
            detail_rows.append(
                {
                    'indikator_id': indicator_id,
                    'wilayah': wilayah,
                    'tahun': tahun_target,
                    'nilai': nilai_target,
                    'tahun_terakhir': tahun_terakhir,
                    'nilai_terakhir': nilai_terakhir,
                    'slope_per_tahun': slope_per_tahun,
                    'r_squared': r_squared,
                    'arah_tren': arah_tren,
                    'catatan': catatan,
                    'insight_text': insight_text,
                    'detail_json': detail_payload,
                }
            )

    if not detail_rows:
        return 0

    detail_df = pd.DataFrame(detail_rows)
    connection.executemany(
        '''
        INSERT INTO proyeksi_detail (indikator_id, wilayah, tahun, nilai, detail_json)
        VALUES (?, ?, ?, ?, ?)
        ''',
        [
            (
                row.indikator_id,
                row.wilayah,
                int(row.tahun),
                float(row.nilai),
                row.detail_json,
            )
            for row in detail_df.itertuples(index=False)
        ],
    )

    grouped = detail_df.groupby(['wilayah', 'tahun'], as_index=False).agg(
        nilai=('nilai', 'mean'),
        tahun_terakhir=('tahun_terakhir', 'max'),
        nilai_terakhir=('nilai_terakhir', 'max'),
        slope_per_tahun=('slope_per_tahun', 'mean'),
        r_squared=('r_squared', 'mean'),
        arah_tren=('arah_tren', 'first'),
        catatan=('catatan', 'first'),
        insight_text=('insight_text', 'first'),
    )

    connection.executemany(
        '''
        INSERT OR REPLACE INTO proyeksi (
            indikator_id, wilayah, tahun, nilai, tahun_terakhir,
            nilai_terakhir, slope_per_tahun, r_squared, arah_tren, catatan, insight_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        [
            (
                indicator_id,
                row.wilayah,
                int(row.tahun),
                float(row.nilai),
                int(row.tahun_terakhir) if pd.notna(row.tahun_terakhir) else None,
                float(row.nilai_terakhir) if pd.notna(row.nilai_terakhir) else None,
                float(row.slope_per_tahun) if pd.notna(row.slope_per_tahun) else None,
                float(row.r_squared) if pd.notna(row.r_squared) else None,
                row.arah_tren,
                row.catatan,
                row.insight_text,
            )
            for row in grouped.itertuples(index=False)
        ],
    )
    return int(len(grouped))


def rebuild_database() -> dict[str, int]:
    if not PROJECTION_CSV.exists():
        raise FileNotFoundError(f'File proyeksi tidak ditemukan: {PROJECTION_CSV}')
    if not HISTORICAL_DIR.exists():
        raise FileNotFoundError(f'Folder data historis tidak ditemukan: {HISTORICAL_DIR}')

    if DB_PATH.exists():
        try:
            DB_PATH.unlink()
        except PermissionError:
            with get_connection() as connection:
                connection.executescript('''
                    DROP TABLE IF EXISTS historis_detail;
                    DROP TABLE IF EXISTS proyeksi_detail;
                    DROP TABLE IF EXISTS historis;
                    DROP TABLE IF EXISTS proyeksi;
                    DROP TABLE IF EXISTS indikator;
                ''')

    projection_df = read_csv_fallback(PROJECTION_CSV)
    projection_df = projection_df.fillna('')

    summary_by_file: dict[str, pd.Series] = {}
    for _, row in projection_df.iterrows():
        file_key = normalize_text(row.get('file_sumber'))
        if not file_key or file_key in summary_by_file:
            continue
        summary_by_file[file_key] = row

    if not summary_by_file:
        raise RuntimeError('CSV proyeksi kosong atau tidak valid')

    counts = {'indikator': 0, 'historis': 0, 'proyeksi': 0, 'file_historis_dilewati': 0}

    with get_connection() as connection:
        ensure_schema(connection)

        indicator_id_by_file: dict[str, int] = {}
        for file_key, row in summary_by_file.items():
            indicator_id = upsert_indicator(connection, row)
            indicator_id_by_file[file_key] = indicator_id
            counts['indikator'] += 1

        for csv_path in sorted(HISTORICAL_DIR.glob('*.csv')):
            file_key = csv_path.name.strip()
            summary_row = summary_by_file.get(file_key)
            if summary_row is None:
                counts['file_historis_dilewati'] += 1
                continue
            indicator_id = indicator_id_by_file[file_key]
            counts['historis'] += load_historical_series(connection, indicator_id, csv_path)

        for file_key, subset in projection_df.groupby(projection_df['file_sumber'].map(normalize_text)):
            if not file_key:
                continue
            indicator_id = indicator_id_by_file.get(file_key)
            if indicator_id is None:
                continue
            counts['proyeksi'] += load_projection_series(connection, indicator_id, subset)

        connection.commit()

    return counts


def ensure_database(force: bool = False) -> dict[str, int]:
    if force or not DB_PATH.exists():
        return rebuild_database()

    with get_connection() as connection:
        ensure_schema(connection)
        indicator_count = connection.execute('SELECT COUNT(*) AS total FROM indikator').fetchone()['total']

    if indicator_count == 0:
        return rebuild_database()

    return {'indikator': int(indicator_count), 'historis': 0, 'proyeksi': 0, 'file_historis_dilewati': 0}


if __name__ == '__main__':
    result = ensure_database(force=True)
    print(result)
