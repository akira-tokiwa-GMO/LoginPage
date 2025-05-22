from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "database.db"


def get_connection(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    """SQLite の接続を取得します。"""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db(db_path: Path | str = DB_PATH) -> None:
    """ユーザーテーブルを作成します。"""
    schema = """
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL CHECK(length(username) <= 50),
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """
    with get_connection(db_path) as conn:
        conn.executescript(schema)
        conn.commit()


def main() -> None:
    """CLI エントリポイント"""
    init_db()
    print("Database initialized")


if __name__ == "__main__":
    main()
