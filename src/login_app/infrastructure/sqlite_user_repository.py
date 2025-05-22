"""SQLite implementation of the user repository."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from login_app.domain.models import User
from login_app.domain.repositories import UserRepository

from .database import DB_PATH, get_connection


class SQLiteUserRepository(UserRepository):
    """Repository that persists users in a SQLite database."""

    def __init__(self, db_path: Path | str = DB_PATH) -> None:
        self.db_path = Path(db_path)

    def create(self, username: str, email: str, password_hash: str) -> User:
        now = datetime.utcnow()
        query = (
            "INSERT INTO user (username, email, password_hash, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?)"
        )
        with get_connection(self.db_path) as conn:
            cursor = conn.execute(query, (username, email, password_hash, now, now))
            conn.commit()
            user_id = cursor.lastrowid
        return User(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            created_at=now,
            updated_at=now,
        )

    def _row_to_user(self, row: tuple[Any, ...]) -> User:
        return User(
            id=row[0],
            username=row[1],
            email=row[2],
            password_hash=row[3],
            created_at=datetime.fromisoformat(row[4]),
            updated_at=datetime.fromisoformat(row[5]),
        )

    def get_by_id(self, user_id: int) -> User | None:
        query = (
            "SELECT id, username, email, password_hash, created_at, updated_at"
            " FROM user WHERE id = ?"
        )
        with get_connection(self.db_path) as conn:
            row = conn.execute(query, (user_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_user(row)

    def get_by_email(self, email: str) -> User | None:
        query = (
            "SELECT id, username, email, password_hash, created_at, updated_at"
            " FROM user WHERE email = ?"
        )
        with get_connection(self.db_path) as conn:
            row = conn.execute(query, (email,)).fetchone()
        if row is None:
            return None
        return self._row_to_user(row)
