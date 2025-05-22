from __future__ import annotations

"""Use case layer for authentication."""

import re
from typing import Any, MutableMapping

from login_app.domain.repositories import UserRepository
from login_app.infrastructure.security.password import hash_password, verify_password


class AuthUsecase:
    """Provide user registration, login and logout operations."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def _check_strength(self, password: str) -> None:
        """Validate password strength and raise ValueError if weak."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must include an uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must include a lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must include a digit")

    def register(self, username: str, email: str, password: str):
        """Create a new user after validating password strength."""
        self._check_strength(password)
        hashed = hash_password(password)
        return self.user_repo.create(username, email, hashed)

    def login(self, email: str, password: str):
        """Authenticate a user by email and password."""
        user = self.user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        return user

    def logout(self, session: MutableMapping[str, Any]) -> None:
        """Remove user information from the given session."""
        session.pop("user_id", None)
