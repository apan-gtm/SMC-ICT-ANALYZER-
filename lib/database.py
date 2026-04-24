"""
lib/database.py
SQLite CRUD untuk riwayat analisa.
DB disimpan di history.db di root project (atau /tmp untuk Streamlit Cloud).
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

# Streamlit Cloud filesystem tidak persistent di root — gunakan /tmp
# Untuk lokal, simpan di direktori project saja.
import os
_IS_CLOUD = os.environ.get("STREAMLIT_SHARING_MODE") or os.environ.get("IS_STREAMLIT_CLOUD")
DB_PATH = Path("/tmp/history.db") if _IS_CLOUD else Path("history.db")


def _conn() -> sqlite3.Connection:
    """Buka koneksi SQLite dengan row_factory."""
    con = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    """Buat tabel jika belum ada."""
    with _conn() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at   TEXT    NOT NULL,
                image_bytes  BLOB    NOT NULL,
                note         TEXT    DEFAULT '',
                analysis_text TEXT   NOT NULL,
                news_json    TEXT    DEFAULT NULL
            )
        """)
        con.commit()


def save_analysis(
    image_bytes: bytes,
    note: str,
    analysis_text: str,
    news_json: str | None,
) -> int:
    """Simpan analisa baru, return id baris baru."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _conn() as con:
        cur = con.execute(
            "INSERT INTO history (created_at, image_bytes, note, analysis_text, news_json) VALUES (?,?,?,?,?)",
            (ts, image_bytes, note, analysis_text, news_json),
        )
        con.commit()
        return cur.lastrowid


def get_all_history() -> list[tuple]:
    """
    Return list (id, created_at, analysis_preview_40, news_json)
    Diurutkan terbaru dulu.
    """
    with _conn() as con:
        rows = con.execute(
            "SELECT id, created_at, SUBSTR(analysis_text,1,40) as preview, news_json "
            "FROM history ORDER BY id DESC"
        ).fetchall()
    return [(r["id"], r["created_at"], r["preview"], r["news_json"]) for r in rows]


def get_analysis_by_id(record_id: int) -> dict | None:
    """Return dict dengan semua field, atau None jika tidak ditemukan."""
    with _conn() as con:
        row = con.execute(
            "SELECT * FROM history WHERE id=?", (record_id,)
        ).fetchone()
    if not row:
        return None
    return {
        "id":            row["id"],
        "created_at":    row["created_at"],
        "image_bytes":   bytes(row["image_bytes"]),
        "note":          row["note"],
        "analysis_text": row["analysis_text"],
        "news_json":     row["news_json"],
    }


def delete_analysis(record_id: int) -> None:
    """Hapus satu record dari DB."""
    with _conn() as con:
        con.execute("DELETE FROM history WHERE id=?", (record_id,))
        con.commit()
