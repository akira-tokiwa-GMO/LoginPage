"""User repository interface."""

from __future__ import annotations

from typing import Protocol

from ..models import User


class UserRepository(Protocol):
    """Interface for user persistence operations."""

    def create(self, username: str, email: str, password_hash: str) -> User:
        """Persist a new user and return the created entity."""

    def get_by_id(self, user_id: int) -> User | None:
        """Return a user by its id."""

    def get_by_email(self, email: str) -> User | None:
        """Return a user by its email address."""
