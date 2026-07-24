from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sys, os, re
from difflib import SequenceMatcher
sys.path.append(os.path.dirname(__file__))
from backend.routes.chat import router as chat_router

from .db import DB_PATH, get_connection
from .loader import ensure_database
from api.routes import router

app = FastAPI(title='SADA-AI Trend Prediction API', version='0.1.0')

app.include_router(chat_router)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get("/")
def root():
    return {
        "service": "SADA AI",
        "status": "Running"
    }


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

        historical_rows = connection.execute(
            '''
            SELECT wilayah, COUNT(*) AS historical_count
            FROM historis
            WHERE indikator_id = ?
            GROUP BY wilayah
            ''',
            (indicator_row['id'],),
        ).fetchall()
        projection_rows = connection.execute(
            '''
            SELECT wilayah, COUNT(*) AS projection_count
            FROM proyeksi
            WHERE indikator_id = ?
            GROUP BY wilayah
            ''',
            (indicator_row['id'],),
        ).fetchall()

        rows = connection.execute(
            '''
            SELECT wilayah FROM historis WHERE indikator_id = ?
            UNION
            SELECT wilayah FROM proyeksi WHERE indikator_id = ?
            ORDER BY wilayah
            ''',
            (indicator_row['id'], indicator_row['id']),
        ).fetchall()

    historical_count_by_region = {row['wilayah']: row['historical_count'] for row in historical_rows}
    projection_count_by_region = {row['wilayah']: row['projection_count'] for row in projection_rows}

    return {
        'indikator': indikator,
        'wilayah': [row['wilayah'] for row in rows],
        'wilayah_detail': [
            {
                'wilayah': row['wilayah'],
                'historical_count': int(historical_count_by_region.get(row['wilayah'], 0)),
                'projection_count': int(projection_count_by_region.get(row['wilayah'], 0)),
            }
            for row in rows
        ],
    }


@app.get('/detail-historis')
def get_historical_detail(indikator: str = Query(..., min_length=1), wilayah: str = Query(..., min_length=1)) -> dict[str, object]:
    ensure_database()
    with get_connection() as connection:
        indicator_row = connection.execute(
            'SELECT id FROM indikator WHERE nama = ?',
            (indikator,),
        ).fetchone()
        if indicator_row is None:
            raise HTTPException(status_code=404, detail='Indikator tidak ditemukan')

        rows = connection.execute(
            '''
            SELECT tahun, nilai, detail_json
            FROM historis_detail
            WHERE indikator_id = ? AND wilayah = ?
            ORDER BY tahun
            ''',
            (indicator_row['id'], wilayah),
        ).fetchall()

    return {
        'indikator': indikator,
        'wilayah': wilayah,
        'detail': [
            {
                'tahun': row['tahun'],
                'nilai': row['nilai'],
                'detail_json': row['detail_json'],
            }
            for row in rows
        ],
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

        historical_detail_rows = connection.execute(
            '''
            SELECT tahun, nilai, detail_json
            FROM historis_detail
            WHERE indikator_id = ? AND wilayah = ?
            ORDER BY tahun
            ''',
            (indicator_row['id'], wilayah),
        ).fetchall()

        projection_rows = connection.execute(
            '''
            SELECT tahun, nilai, tahun_terakhir, nilai_terakhir, slope_per_tahun, r_squared, arah_tren, catatan, insight_text
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
            'insight_text': first_row['insight_text'],
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
        'historis_detail': [
            {
                'tahun': row['tahun'],
                'nilai': row['nilai'],
                'detail_json': row['detail_json'],
            }
            for row in historical_detail_rows
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


def _trend_match_score(indicator: str, question: str) -> float:
    """Match a natural-language trend request to a stored model indicator."""
    question_text = re.sub(r'[^a-z0-9]+', ' ', question.lower()).strip()
    indicator_text = re.sub(r'[^a-z0-9]+', ' ', indicator.lower()).strip()
    aliases = {'kemisikinan': 'kemiskinan', 'kemiskinan': 'miskin', 'miskin': 'miskin'}
    question_tokens = [aliases.get(token, token) for token in question_text.split()]
    indicator_tokens = indicator_text.split()
    score = 0.0
    for token in question_tokens:
        if len(token) < 4 or token in {'tren', 'trend', 'tahun', 'lihat', 'tampilkan', 'data'}:
            continue
        if token in indicator_tokens or token in indicator_text:
            score += 20
        score += max((SequenceMatcher(None, token, candidate).ratio() for candidate in indicator_tokens), default=0) * 4
    return score


def _build_projection_insight(summary: dict | None, target: dict | None) -> str:
    """Build a safe insight only from fields already present in projection JSON."""
    if not summary:
        return ''
    direction = summary.get('arah_tren') or 'tidak tersedia'
    last_year = summary.get('tahun_terakhir')
    last_value = summary.get('nilai_terakhir')
    r_squared = summary.get('r_squared')
    sentences = [f"Model proyeksi menunjukkan arah tren {direction} berdasarkan data historis yang tersedia."]
    if last_year is not None and last_value is not None:
        sentences.append(f"Nilai historis terakhir yang digunakan model adalah {last_value} pada {last_year}.")
    if target:
        sentences.append(f"Untuk {target['tahun']}, nilai proyeksi model adalah {target['nilai']}.")
    if r_squared is not None:
        sentences.append(f"Nilai R² model tercatat {r_squared}; proyeksi perlu dibaca sebagai estimasi, bukan realisasi data.")
    else:
        sentences.append('Proyeksi perlu dibaca sebagai estimasi, bukan realisasi data.')
    return ' '.join(sentences)


@app.get('/trend-chat')
def get_trend_for_chat(question: str = Query(..., min_length=3)) -> dict[str, object]:
    """Return the existing Trend Prediction series selected from a chat question."""
    if not re.search(r'\btren(?:d)?\b', question, re.IGNORECASE):
        return {'matched': False}

    ensure_database()
    with get_connection() as connection:
        indicators = [row['nama'] for row in connection.execute('SELECT nama FROM indikator').fetchall()]

    if not indicators:
        return {'matched': False}

    indicator = max(indicators, key=lambda item: _trend_match_score(item, question))
    if _trend_match_score(indicator, question) < 10:
        return {'matched': False}

    requested_region = None
    question_lower = question.lower()
    with get_connection() as connection:
        region_rows = connection.execute(
            '''
            SELECT wilayah FROM historis WHERE indikator_id = (SELECT id FROM indikator WHERE nama = ?)
            UNION
            SELECT wilayah FROM proyeksi WHERE indikator_id = (SELECT id FROM indikator WHERE nama = ?)
            ''',
            (indicator, indicator),
        ).fetchall()
    regions = [row['wilayah'] for row in region_rows]
    for region in regions:
        if region and str(region).lower() in question_lower:
            requested_region = region
            break
    if requested_region is None:
        requested_region = next((region for region in regions if str(region).strip().lower() in {'aceh', 'provinsi aceh'}), regions[0] if regions else None)
    if requested_region is None:
        return {'matched': False}

    payload = get_data(indikator=indicator, wilayah=requested_region)
    requested_year_match = re.search(r'\b20\d{2}\b', question)
    requested_year = int(requested_year_match.group()) if requested_year_match else None
    target = next(
        (point for point in [*payload['proyeksi'], *payload['historis']] if point['tahun'] == requested_year),
        None,
    )
    # Some legacy projection CSVs have an empty `insight_text`. Keep the
    # endpoint useful by deriving a transparent, deterministic insight from
    # the same projection JSON instead of hiding the insight panel entirely.
    if not (payload.get('ringkasan') or {}).get('insight_text'):
        payload['ringkasan']['insight_text'] = _build_projection_insight(payload.get('ringkasan'), target)
    return {
        'matched': True,
        'requested_year': requested_year,
        'target': target,
        **payload,
    }
