import pytest
import sqlite3 # For raising sqlite3.Error
from unittest.mock import patch, MagicMock

from src.auth.services import create_user, authenticate_user
# Schemas might be needed for isinstance or if their instances are directly manipulated.
# For mocking their validate() and errors, we might not need to import the actual classes.

# --- Tests for create_user ---

@patch('src.auth.services.get_db_connection')
@patch('src.auth.services.hash_password')
@patch('src.auth.services.UserRegistrationSchema')
def test_create_user_successful(MockUserRegistrationSchema, mock_hash_password, mock_get_db_connection):
    # Mock Schema validation
    mock_schema_instance = MockUserRegistrationSchema.return_value
    mock_schema_instance.validate.return_value = {} # Marshmallow success (empty dict)

    # Mock password hashing
    mock_hash_password.return_value = "hashed_password_dummy"

    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock email check (email not found)
    mock_cursor.fetchone.return_value = None 
    # Mock insert (lastrowid)
    mock_cursor.lastrowid = 1

    result = create_user("testuser", "test@example.com", "password123")

    MockUserRegistrationSchema.assert_called_once()
    mock_schema_instance.validate.assert_called_once_with({
        "username": "testuser", "email": "test@example.com", "password": "password123"
    })
    mock_hash_password.assert_called_once_with("password123")
    mock_get_db_connection.assert_called_once()
    mock_conn.cursor.assert_called_once()
    
    # Check SELECT for email and INSERT for user
    assert mock_cursor.execute.call_count == 2
    mock_cursor.execute.assert_any_call("SELECT id FROM user WHERE email = ?", ("test@example.com",))
    mock_cursor.execute.assert_any_call(
        "INSERT INTO user (username, email, hashed_password) VALUES (?, ?, ?)",
        ("testuser", "test@example.com", "hashed_password_dummy")
    )
    mock_conn.commit.assert_called_once()
    assert result == {"success": True, "user_id": 1}

@patch('src.auth.services.get_db_connection')
@patch('src.auth.services.UserRegistrationSchema')
def test_create_user_schema_validation_failure(MockUserRegistrationSchema, mock_get_db_connection):
    mock_schema_instance = MockUserRegistrationSchema.return_value
    sample_errors = {"username": ["Too short"]}
    mock_schema_instance.validate.return_value = sample_errors # Marshmallow failure (dict with errors)

    result = create_user("tu", "test@example.com", "password123")

    MockUserRegistrationSchema.assert_called_once()
    mock_schema_instance.validate.assert_called_once()
    mock_get_db_connection.assert_not_called()
    assert result == {"success": False, "errors": sample_errors}

@patch('src.auth.services.get_db_connection')
@patch('src.auth.services.hash_password')
@patch('src.auth.services.UserRegistrationSchema')
def test_create_user_email_already_exists(MockUserRegistrationSchema, mock_hash_password, mock_get_db_connection):
    mock_schema_instance = MockUserRegistrationSchema.return_value
    mock_schema_instance.validate.return_value = {} # Success

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,) # Email exists

    result = create_user("testuser", "test@example.com", "password123")

    mock_get_db_connection.assert_called_once()
    mock_cursor.execute.assert_called_once_with("SELECT id FROM user WHERE email = ?", ("test@example.com",))
    # Ensure INSERT was not called
    insert_call_present = any(
        "INSERT INTO user" in call.args[0] for call in mock_cursor.execute.call_args_list
    )
    assert not insert_call_present
    assert result == {"success": False, "errors": {"email": "Email already registered."}}


@patch('src.auth.services.get_db_connection')
@patch('src.auth.services.hash_password')
@patch('src.auth.services.UserRegistrationSchema')
def test_create_user_database_error_on_insert(MockUserRegistrationSchema, mock_hash_password, mock_get_db_connection):
    mock_schema_instance = MockUserRegistrationSchema.return_value
    mock_schema_instance.validate.return_value = {} # Success

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # First call to execute (email check) is fine
    mock_cursor.fetchone.return_value = None 
    # Second call to execute (INSERT) raises error
    mock_cursor.execute.side_effect = [None, sqlite3.Error("Simulated DB error on insert")]


    result = create_user("testuser", "test@example.com", "password123")
    
    mock_get_db_connection.assert_called_once()
    assert mock_cursor.execute.call_count == 2 # SELECT and failing INSERT
    mock_conn.commit.assert_not_called() # Should not commit if insert fails
    mock_conn.close.assert_called_once() # Ensure connection is closed
    assert result == {"success": False, "errors": {"database": "A database error occurred."}}


# --- Tests for authenticate_user ---

@patch('src.auth.services.get_db_connection')
@patch('src.auth.services.check_password') # from src.models, but imported into services namespace
@patch('src.auth.services.UserLoginSchema') # Custom schema
def test_authenticate_user_successful(MockUserLoginSchema, mock_check_password, mock_get_db_connection):
    # Mock Schema validation (custom schema)
    mock_schema_instance = MockUserLoginSchema.return_value
    mock_schema_instance.validate.return_value = True # Custom schema success
    mock_schema_instance.errors = {}

    # Mock DB
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Mock user data from DB
    mock_user_row = {"id": 1, "username": "testuser", "email": "test@example.com", "hashed_password": "hashed_pw_from_db"}
    mock_cursor.fetchone.return_value = mock_user_row
    
    # Mock password check
    mock_check_password.return_value = True

    result = authenticate_user("test@example.com", "password123")

    MockUserLoginSchema.assert_called_once_with(email="test@example.com", password="password123")
    mock_schema_instance.validate.assert_called_once()
    mock_get_db_connection.assert_called_once()
    mock_cursor.execute.assert_called_once_with(
        "SELECT id, username, email, hashed_password FROM user WHERE email = ?", 
        ("test@example.com",)
    )
    mock_check_password.assert_called_once_with("password123", "hashed_pw_from_db")
    assert result == {
        "success": True, 
        "user": {"id": 1, "username": "testuser", "email": "test@example.com"}
    }

@patch('src.auth.services.get_db_connection')
@patch('src.auth.services.UserLoginSchema')
def test_authenticate_user_schema_validation_failure(MockUserLoginSchema, mock_get_db_connection):
    mock_schema_instance = MockUserLoginSchema.return_value
    mock_schema_instance.validate.return_value = False # Custom schema failure
    mock_schema_instance.errors = {"email": ["Invalid format"]}

    result = authenticate_user("invalid-email", "password123")

    MockUserLoginSchema.assert_called_once()
    mock_schema_instance.validate.assert_called_once()
    mock_get_db_connection.assert_not_called()
    assert result == {"success": False, "errors": {"email": ["Invalid format"]}}

@patch('src.auth.services.get_db_connection')
@patch('src.auth.services.check_password')
@patch('src.auth.services.UserLoginSchema')
def test_authenticate_user_not_found(MockUserLoginSchema, mock_check_password, mock_get_db_connection):
    mock_schema_instance = MockUserLoginSchema.return_value
    mock_schema_instance.validate.return_value = True # Success
    mock_schema_instance.errors = {}

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None # User not found

    result = authenticate_user("nonexistent@example.com", "password123")

    mock_get_db_connection.assert_called_once()
    mock_check_password.assert_not_called()
    assert result == {"success": False, "errors": {"form": "Invalid email or password."}}

@patch('src.auth.services.get_db_connection')
@patch('src.auth.services.check_password')
@patch('src.auth.services.UserLoginSchema')
def test_authenticate_user_incorrect_password(MockUserLoginSchema, mock_check_password, mock_get_db_connection):
    mock_schema_instance = MockUserLoginSchema.return_value
    mock_schema_instance.validate.return_value = True # Success
    mock_schema_instance.errors = {}

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    mock_user_row = {"id": 1, "username": "testuser", "email": "test@example.com", "hashed_password": "hashed_pw_from_db"}
    mock_cursor.fetchone.return_value = mock_user_row
    
    mock_check_password.return_value = False # Incorrect password

    result = authenticate_user("test@example.com", "wrongpassword")

    mock_get_db_connection.assert_called_once()
    mock_check_password.assert_called_once_with("wrongpassword", "hashed_pw_from_db")
    assert result == {"success": False, "errors": {"form": "Invalid email or password."}}


@patch('src.auth.services.get_db_connection')
@patch('src.auth.services.UserLoginSchema')
def test_authenticate_user_database_error_on_fetch(MockUserLoginSchema, mock_get_db_connection):
    mock_schema_instance = MockUserLoginSchema.return_value
    mock_schema_instance.validate.return_value = True # Success
    mock_schema_instance.errors = {}

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    mock_cursor.execute.side_effect = sqlite3.Error("Simulated DB error on fetch")

    result = authenticate_user("test@example.com", "password123")
    
    mock_get_db_connection.assert_called_once()
    mock_conn.close.assert_called_once() # Ensure connection is closed
    assert result == {"success": False, "errors": {"database": "A database error occurred."}}
```
