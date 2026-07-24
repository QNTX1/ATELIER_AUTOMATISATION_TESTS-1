"""
storage.py
Persistance SQLite de l'historique des runs de tests.
Chaque run est stocké avec ses champs indexés + le JSON complet (colonne payload).
"""
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "runs.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            passed INTEGER NOT NULL,
            failed INTEGER NOT NULL,
            total INTEGER NOT NULL,
            error_rate REAL NOT NULL,
            availability REAL NOT NULL,
            latency_ms_avg REAL NOT NULL,
            latency_ms_p95 REAL NOT NULL,
            payload TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_run(run):
    conn = get_connection()
    s = run["summary"]
    conn.execute(
        """INSERT INTO runs
           (api, timestamp, passed, failed, total, error_rate, availability,
            latency_ms_avg, latency_ms_p95, payload)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            run["api"], run["timestamp"], s["passed"], s["failed"], s["total"],
            s["error_rate"], s["availability"], s["latency_ms_avg"],
            s["latency_ms_p95"], json.dumps(run, ensure_ascii=False),
        ),
    )
    conn.commit()
    conn.close()


def list_runs(limit=50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_last_run():
    runs = list_runs(limit=1)
    return runs[0] if runs else None
