import pytest
from src.schemas import UserRegistrationSchema, UserLoginSchema

# --- Tests for UserRegistrationSchema (Marshmallow-based - Refactored) ---

def test_user_registration_schema_valid_data():
    """
    Tests UserRegistrationSchema with complete and valid data.
    """
    valid_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password123!",
        "password_confirm": "Password123!"
    }
    schema = UserRegistrationSchema()
    errors = schema.validate(valid_data)
    assert not errors, f"Validation failed for valid data: {errors}"

# Username validation tests
@pytest.mark.parametrize("username, expected_error_part", [
    ("", "Username must be between 1 and 50 characters."),  # Empty, also too short
    ("a"*51, "Username must be between 1 and 50 characters."), # Too long
])
def test_user_registration_schema_invalid_username(username, expected_error_part):
    data = {
        "username": username, 
        "email": "test@example.com", 
        "password": "Password123!",
        "password_confirm": "Password123!"
    }
    schema = UserRegistrationSchema()
    errors = schema.validate(data)
    assert "username" in errors, f"Error not found for username: '{username}'"
    assert any(expected_error_part in error for error in errors["username"]), \
           f"'{expected_error_part}' not found in errors: {errors['username']}"


# Email validation tests
@pytest.mark.parametrize("email, expected_error_part", [
    ("", "Missing data for required field."), # Marshmallow default for required + empty
    ("invalid-email", "Not a valid email address."),
])
def test_user_registration_schema_invalid_email(email, expected_error_part):
    data = {
        "username": "testuser", 
        "email": email, 
        "password": "Password123!",
        "password_confirm": "Password123!"
    }
    schema = UserRegistrationSchema()
    errors = schema.validate(data)
    # For empty required field, Marshmallow puts a generic "Missing data for required field."
    # For invalid format on a non-empty field, it's "Not a valid email address."
    # If the field is empty and Email validator runs, it might say "Not a valid email address."
    # Let's check if 'email' is in errors and if the message is somewhat right
    assert "email" in errors, f"Error not found for email: '{email}'"
    assert any(expected_error_part in error for error in errors["email"]), \
           f"'{expected_error_part}' not found in errors: {errors['email']}"


# Password strength validation tests
@pytest.mark.parametrize("password, expected_error_parts", [
    ("", ["Password must be at least 8 characters long."]), # Empty implies all rules failed potentially
    ("short", ["Password must be at least 8 characters long."]),
    ("nouppercase1!", ["Password must contain at least one uppercase letter."]),
    ("NOLOWERCASE1!", ["Password must contain at least one lowercase letter."]),
    ("NoDigitHere!", ["Password must contain at least one digit."]),
    ("NoSpecial123", ["Password must contain at least one special character."]),
    ("WeakPwd", [ # Multiple failures
        "Password must be at least 8 characters long.",
        "Password must contain at least one uppercase letter.", # Assuming 'W' is not uppercase for this example
        "Password must contain at least one digit.",
        "Password must contain at least one special character."
    ])
])
def test_user_registration_schema_password_strength(password, expected_error_parts):
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": password,
        "password_confirm": password # Assume confirm matches for this test
    }
    # Adjusting the "WeakPwd" case for more realistic multiple failures
    if password == "WeakPwd":
        data["password_confirm"] = "WeakPwd" # ensure confirm matches
    
    schema = UserRegistrationSchema()
    errors = schema.validate(data)
    assert "password" in errors, f"Password validation error not found for: '{password}'"
    for expected_part in expected_error_parts:
        assert any(expected_part in error_msg for error_msg in errors["password"]), \
               f"Expected error part '{expected_part}' not found in {errors['password']} for password '{password}'"

# Password confirmation test
def test_user_registration_schema_password_mismatch():
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password123!",
        "password_confirm": "PasswordDoesNotMatch123!"
    }
    schema = UserRegistrationSchema()
    errors = schema.validate(data)
    assert "password_confirm" in errors, "Error not found for password_confirm mismatch"
    assert "Passwords do not match." in errors["password_confirm"]

# Required fields tests
@pytest.mark.parametrize("missing_field", ["username", "email", "password", "password_confirm"])
def test_user_registration_schema_missing_fields(missing_field):
    valid_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password123!",
        "password_confirm": "Password123!"
    }
    data = valid_data.copy()
    del data[missing_field] # Remove one required field
    
    schema = UserRegistrationSchema()
    errors = schema.validate(data)
    assert missing_field in errors, f"Error not found for missing field: {missing_field}"
    assert "Missing data for required field." in errors[missing_field]

# Multiple errors test (general, different from specific password multi-error)
def test_user_registration_schema_multiple_field_errors():
    data = {
        "username": "a"*51,         # Too long
        "email": "invalid",         # Invalid format
        "password": "short",        # Too short (and other strength issues)
        "password_confirm": "short" # Confirm matches password, but password itself is weak
    }
    schema = UserRegistrationSchema()
    errors = schema.validate(data)
    assert "username" in errors
    assert "email" in errors
    assert "password" in errors # Password errors will be a list from validate_password_strength
    
    assert any("Username must be between 1 and 50 characters." in e for e in errors["username"])
    assert any("Not a valid email address." in e for e in errors["email"])
    assert any("Password must be at least 8 characters long." in e for e in errors["password"])
    # We don't need to check all password strength errors here, just that the field has errors.

# --- Tests for UserLoginSchema (Custom schema) ---

def test_user_login_schema_valid_data():
    """
    Tests UserLoginSchema with valid email and password.
    """
    schema = UserLoginSchema(email="test@example.com", password="password123")
    assert schema.validate() is True, f"Validation failed for valid data: {schema.errors}"
    assert not schema.errors, f"Errors dictionary should be empty for valid data: {schema.errors}"

# Email validation tests for UserLoginSchema
def test_user_login_schema_invalid_email_empty():
    schema = UserLoginSchema(email="", password="password123")
    assert schema.validate() is False
    assert "email" in schema.errors
    assert schema.errors["email"] == "Email is required."

def test_user_login_schema_invalid_email_format():
    schema = UserLoginSchema(email="invalid-email", password="password123")
    assert schema.validate() is False
    assert "email" in schema.errors
    assert schema.errors["email"] == "Invalid email format."

# Password validation tests for UserLoginSchema
def test_user_login_schema_invalid_password_empty():
    schema = UserLoginSchema(email="test@example.com", password="")
    assert schema.validate() is False
    assert "password" in schema.errors
    assert schema.errors["password"] == "Password is required."

# Multiple errors test for UserLoginSchema
def test_user_login_schema_multiple_errors():
    schema = UserLoginSchema(email="invalid", password="")
    assert schema.validate() is False
    assert "email" in schema.errors
    assert "password" in schema.errors
    assert schema.errors["email"] == "Invalid email format."
    assert schema.errors["password"] == "Password is required."

# Test that errors are reset on subsequent validate calls for UserLoginSchema
def test_user_login_schema_errors_reset():
    schema = UserLoginSchema(email="", password="")
    # First validation
    assert schema.validate() is False
    assert "email" in schema.errors
    assert "password" in schema.errors

    # Correct the data and re-validate
    schema.email = "correct@example.com"
    schema.password = "correctpassword"
    assert schema.validate() is True
    assert not schema.errors # Errors should be cleared
```
