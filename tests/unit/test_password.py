from login_app.infrastructure.security.password import hash_password, verify_password


def test_hash_and_verify_password():
    password = "secret123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)
