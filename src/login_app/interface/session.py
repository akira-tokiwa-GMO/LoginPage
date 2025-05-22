"""Flask session management utilities."""

from __future__ import annotations

import secrets

from flask import Flask, abort, request, session


def init_session(app: Flask) -> None:
    """Configure session handling with CSRF protection."""
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)

    @app.before_request
    def csrf_protect() -> None:
        if request.method == "POST":
            token = session.get("csrf_token")
            form_token = request.form.get("csrf_token")
            if not token or token != form_token:
                abort(400)

    @app.context_processor
    def inject_csrf_token() -> dict[str, str]:
        token = session.get("csrf_token")
        if token is None:
            token = secrets.token_hex(16)
            session["csrf_token"] = token
        return {"csrf_token": token}
