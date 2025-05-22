import pytest

from login_app.infrastructure.database import init_db
from login_app.infrastructure.sqlite_user_repository import SQLiteUserRepository
from login_app.usecases import AuthUsecase


def setup_usecase(tmp_path):
    db = tmp_path / "test.db"
    init_db(db)
    repo = SQLiteUserRepository(db)
    return AuthUsecase(repo)


def test_register_and_login(tmp_path):
    uc = setup_usecase(tmp_path)
    user = uc.register("alice", "alice@example.com", "Strong123")
    logged_in = uc.login("alice@example.com", "Strong123")
    assert logged_in == user


def test_register_weak_password(tmp_path):
    uc = setup_usecase(tmp_path)
    with pytest.raises(ValueError):
        uc.register("bob", "bob@example.com", "weak")


def test_login_invalid_password(tmp_path):
    uc = setup_usecase(tmp_path)
    uc.register("carol", "carol@example.com", "Strong123")
    with pytest.raises(ValueError):
        uc.login("carol@example.com", "wrong")


def test_logout():
    uc = AuthUsecase(None)  # type: ignore
    session = {"user_id": 1}
    uc.logout(session)
    assert "user_id" not in session
