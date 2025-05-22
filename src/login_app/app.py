from __future__ import annotations

"""Flask application factory."""

from pathlib import Path

from flask import Flask

from .infrastructure.database import DB_PATH, init_db
from .infrastructure.sqlite_user_repository import SQLiteUserRepository
from .interface.session import init_session
from .interfaces.controllers.auth_controller import create_auth_blueprint
from .interfaces.controllers.dashboard_controller import create_dashboard_blueprint
from .usecases import AuthUsecase


def create_app(db_path: Path | str = DB_PATH) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.setdefault("SECRET_KEY", "dev-secret")
    init_session(app)
    init_db(db_path)
    user_repo = SQLiteUserRepository(db_path)
    auth_uc = AuthUsecase(user_repo)
    app.register_blueprint(create_auth_blueprint(auth_uc))
    app.register_blueprint(create_dashboard_blueprint(user_repo))
    return app
