from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .db import DB_PATH, get_connection
from .loader import ensure_database

app = FastAPI(title='SADA-AI Trend Prediction API', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
def startup_event() -> None:
    ensure_database()


@app.get('/indikator')
def list_indikator() -> list[dict[str, str | None]]:
    ensure_database()
    with get_connection() as connection:
        rows = connection.execute(
            '''
            SELECT nama, file_sumber, level_wilayah, satuan
            FROM indikator
            ORDER BY nama
            '''
        ).fetchall()

    return [
        {
            'indikator': row['nama'],
            'file_sumber': row['file_sumber'],
            'level_wilayah': row['level_wilayah'],
            'satuan': row['satuan'],
        }
        for row in rows
    ]


@app.get('/wilayah')
def list_wilayah(indikator: str = Query(..., min_length=1)) -> dict[str, object]:
    ensure_database()
    with get_connection() as connection:
        indicator_row = connection.execute(
            'SELECT id, nama FROM indikator WHERE nama = ?',
            (indikator,),
        ).fetchone()
        if indicator_row is None:
            raise HTTPException(status_code=404, detail='Indikator tidak ditemukan')

        rows = connection.execute(
            '''
            SELECT wilayah FROM historis WHERE indikator_id = ?
            UNION
            SELECT wilayah FROM proyeksi WHERE indikator_id = ?
            ORDER BY wilayah
            ''',
            (indicator_row['id'], indicator_row['id']),
        ).fetchall()

    return {
        'indikator': indikator,
        'wilayah': [row['wilayah'] for row in rows],
    }


@app.get('/data')
def get_data(
    indikator: str = Query(..., min_length=1),
    wilayah: str = Query(..., min_length=1),
) -> dict[str, object]:
    ensure_database()
    with get_connection() as connection:
        indicator_row = connection.execute(
            'SELECT id, nama, file_sumber, level_wilayah, satuan FROM indikator WHERE nama = ?',
            (indikator,),
        ).fetchone()
        if indicator_row is None:
            raise HTTPException(status_code=404, detail='Indikator tidak ditemukan')

        historical_rows = connection.execute(
            '''
            SELECT tahun, nilai
            FROM historis
            WHERE indikator_id = ? AND wilayah = ?
            ORDER BY tahun
            ''',
            (indicator_row['id'], wilayah),
        ).fetchall()

        projection_rows = connection.execute(
            '''
            SELECT tahun, nilai, tahun_terakhir, nilai_terakhir, slope_per_tahun, r_squared, arah_tren, catatan
            FROM proyeksi
            WHERE indikator_id = ? AND wilayah = ?
            ORDER BY tahun
            ''',
            (indicator_row['id'], wilayah),
        ).fetchall()

    if not historical_rows and not projection_rows:
        raise HTTPException(status_code=404, detail='Data untuk wilayah tersebut tidak ditemukan')

    summary = None
    if projection_rows:
        first_row = projection_rows[0]
        summary = {
            'tahun_terakhir': first_row['tahun_terakhir'],
            'nilai_terakhir': first_row['nilai_terakhir'],
            'slope_per_tahun': first_row['slope_per_tahun'],
            'r_squared': first_row['r_squared'],
            'arah_tren': first_row['arah_tren'],
            'catatan': first_row['catatan'],
        }

    return {
        'indikator': {
            'nama': indicator_row['nama'],
            'file_sumber': indicator_row['file_sumber'],
            'level_wilayah': indicator_row['level_wilayah'],
            'satuan': indicator_row['satuan'],
        },
        'wilayah': wilayah,
        'ringkasan': summary,
        'historis': [
            {
                'tahun': row['tahun'],
                'nilai': row['nilai'],
                'tipe': 'historis',
            }
            for row in historical_rows
        ],
        'proyeksi': [
            {
                'tahun': row['tahun'],
                'nilai': row['nilai'],
                'tipe': 'proyeksi',
            }
            for row in projection_rows
        ],
    }
