from login_app.infrastructure.database import init_db
from login_app.infrastructure.sqlite_user_repository import SQLiteUserRepository


def test_create_and_get_by_email(tmp_path):
    db_file = tmp_path / "test.db"
    init_db(db_file)
    repo = SQLiteUserRepository(db_file)

    user = repo.create("alice", "alice@example.com", "hash")
    assert user.id is not None
    fetched = repo.get_by_email("alice@example.com")
    assert fetched == user


def test_get_by_id(tmp_path):
    db_file = tmp_path / "test.db"
    init_db(db_file)
    repo = SQLiteUserRepository(db_file)

    user = repo.create("bob", "bob@example.com", "hash")
    fetched = repo.get_by_id(user.id)
    assert fetched == user
