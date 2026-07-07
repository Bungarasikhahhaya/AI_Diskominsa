from pathlib import Path
import sqlite3

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = Path(__file__).resolve().parent
DB_PATH = BACKEND_DIR / 'trend_prediction.db'
PROJECTION_CSV = ROOT_DIR / 'hasil_proyeksi' / 'proyeksi_semua_indikator.csv'
HISTORICAL_DIR = ROOT_DIR / 'dataset_bersih'


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    return connection


def ensure_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        '''
        CREATE TABLE IF NOT EXISTS indikator (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL UNIQUE,
            file_sumber TEXT,
            level_wilayah TEXT,
            satuan TEXT
        );

        CREATE TABLE IF NOT EXISTS historis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indikator_id INTEGER NOT NULL,
            wilayah TEXT NOT NULL,
            tahun INTEGER NOT NULL,
            nilai REAL NOT NULL,
            UNIQUE(indikator_id, wilayah, tahun),
            FOREIGN KEY (indikator_id) REFERENCES indikator (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS proyeksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indikator_id INTEGER NOT NULL,
            wilayah TEXT NOT NULL,
            tahun INTEGER NOT NULL,
            nilai REAL NOT NULL,
            tahun_terakhir INTEGER,
            nilai_terakhir REAL,
            slope_per_tahun REAL,
            r_squared REAL,
            arah_tren TEXT,
            catatan TEXT,
            UNIQUE(indikator_id, wilayah, tahun),
            FOREIGN KEY (indikator_id) REFERENCES indikator (id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_indikator_nama ON indikator (nama);
        CREATE INDEX IF NOT EXISTS idx_historis_indikator_wilayah ON historis (indikator_id, wilayah);
        CREATE INDEX IF NOT EXISTS idx_proyeksi_indikator_wilayah ON proyeksi (indikator_id, wilayah);
        '''
    )
