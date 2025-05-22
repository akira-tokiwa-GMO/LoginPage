import pytest
from flask import session, url_for # url_for is needed to check redirect locations

# Helper function to extract flashed messages (if needed, typically they are in response.data)
# For tests, often easier to follow redirects and check the next page's content.
# However, if a redirect target doesn't display the message, or for non-redirect POSTs,
# accessing messages before next request might be needed. Flask's test client handles cookies
# (and thus session) automatically, so flashed messages should appear on the next GET.

# --- Test Registration (/auth/register) ---

def test_get_registration_page(client):
    """Test GET /auth/register renders the registration page."""
    response = client.get(url_for('auth.register'))
    assert response.status_code == 200
    assert b"Register" in response.data
    assert b"Username" in response.data
    assert b"Password" in response.data
    assert b"Confirm Password" in response.data

def test_successful_registration(client):
    """Test POST /auth/register with valid data."""
    response = client.post(url_for('auth.register'), data={
        "username": "testuser_reg",
        "email": "test_reg@example.com",
        "password": "Password123!",
        "password_confirm": "Password123!"
    }, follow_redirects=True) # follow_redirects is False by default

    # My current register route returns JSON, not a redirect to login.
    # It returns a 201 status code.
    assert response.status_code == 201 
    json_data = response.get_json()
    assert json_data["success"] is True
    assert "User registered successfully" in json_data["message"]
    assert "user_id" in json_data
    # To verify user creation, we can try to log in with this user later.

def test_registration_validation_errors(client):
    """Test POST /auth/register with invalid data (passwords don't match)."""
    response = client.post(url_for('auth.register'), data={
        "username": "testuser_valid_err",
        "email": "test_valid_err@example.com",
        "password": "Password123!",
        "password_confirm": "WrongPassword!"
    })
    # My current register route returns JSON with errors and 400 status
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False
    assert "password_confirm" in json_data["errors"]
    assert "Passwords do not match." in json_data["errors"]["password_confirm"]

    # Test with other validation errors (e.g., username too short from schema)
    response = client.post(url_for('auth.register'), data={
        "username": "", # Empty, fails min=1
        "email": "test_valid_err2@example.com",
        "password": "Password123!",
        "password_confirm": "Password123!"
    })
    assert response.status_code == 400 # Assuming UserRegistrationSchema raises error before service call
    json_data = response.get_json() # service returns JSON on schema failure
    assert json_data["success"] is False
    assert "username" in json_data["errors"] 
    assert "Username must be between 1 and 50 characters." in json_data["errors"]["username"][0]


def test_registration_email_exists(client):
    """Test POST /auth/register with an email that already exists."""
    # First, register a user
    client.post(url_for('auth.register'), data={
        "username": "existinguser",
        "email": "exists@example.com",
        "password": "Password123!",
        "password_confirm": "Password123!"
    }) # Assuming this was successful (201)

    # Attempt to register another user with the same email
    response = client.post(url_for('auth.register'), data={
        "username": "anotheruser",
        "email": "exists@example.com", # Same email
        "password": "Password456!",
        "password_confirm": "Password456!"
    })
    # My service returns 409 for existing email
    assert response.status_code == 409 
    json_data = response.get_json()
    assert json_data["success"] is False
    assert "email" in json_data["errors"]
    assert "Email already registered." in json_data["errors"]["email"]

# --- Test Login (/auth/login) ---

def test_get_login_page(client):
    """Test GET /auth/login renders the login page."""
    response = client.get(url_for('auth.login'))
    assert response.status_code == 200
    assert b"Login" in response.data
    assert b"Email" in response.data
    assert b"Password" in response.data

def test_successful_login(client):
    """Test POST /auth/login with correct credentials."""
    # 1. Register a user first to ensure they exist
    reg_response = client.post(url_for('auth.register'), data={
        "username": "logintestuser",
        "email": "login@example.com",
        "password": "LoginPassword123!",
        "password_confirm": "LoginPassword123!"
    })
    assert reg_response.status_code == 201 # Ensure registration was successful

    # 2. Attempt login
    response = client.post(url_for('auth.login'), data={
        "email": "login@example.com",
        "password": "LoginPassword123!"
    }, follow_redirects=False) # Test the redirect itself

    assert response.status_code == 302
    # My login route redirects to url_for('hello')
    assert response.location == url_for('hello')

    # Check session data after redirect
    with client.session_transaction() as sess:
        assert sess.get('user_id') is not None
        assert sess.get('username') == "logintestuser"

    # Check if flashed message appears on the target page
    redirect_response = client.get(response.location) # Follow the redirect
    assert redirect_response.status_code == 200
    assert b"Login successful!" in redirect_response.data # Flashed message

def test_login_user_not_found(client):
    """Test POST /auth/login with credentials for a non-existent user."""
    response = client.post(url_for('auth.login'), data={
        "email": "nosuchuser@example.com",
        "password": "Password123!"
    })
    assert response.status_code == 400 # Or 200 if re-rendering with errors
    assert b"Invalid email or password." in response.data # Check for error message in HTML
    with client.session_transaction() as sess:
        assert 'user_id' not in sess

def test_login_incorrect_password(client):
    """Test POST /auth/login with correct email but incorrect password."""
    # 1. Register user
    client.post(url_for('auth.register'), data={
        "username": "incorrectpassuser",
        "email": "incorrectpass@example.com",
        "password": "CorrectPassword123!",
        "password_confirm": "CorrectPassword123!"
    })

    # 2. Attempt login with wrong password
    response = client.post(url_for('auth.login'), data={
        "email": "incorrectpass@example.com",
        "password": "IncorrectPassword!"
    })
    assert response.status_code == 400 # Or 200
    assert b"Invalid email or password." in response.data
    with client.session_transaction() as sess:
        assert 'user_id' not in sess

def test_login_missing_fields(client):
    """Test POST /auth/login with missing email or password."""
    # Missing password
    response_no_pass = client.post(url_for('auth.login'), data={
        "email": "test@example.com",
        "password": "" # Missing password
    })
    assert response_no_pass.status_code == 400
    assert b"Both email and password are required." in response_no_pass.data # Check for flashed message on re-render

    # Missing email
    response_no_email = client.post(url_for('auth.login'), data={
        "email": "", # Missing email
        "password": "password123"
    })
    assert response_no_email.status_code == 400
    assert b"Both email and password are required." in response_no_email.data

# --- Test Logout (/auth/logout) ---

def test_logout(client):
    """Test POST /auth/logout logs out the user."""
    # 1. Register and Login a user
    client.post(url_for('auth.register'), data={
        "username": "logoutuser",
        "email": "logout@example.com",
        "password": "LogoutPassword123!",
        "password_confirm": "LogoutPassword123!"
    })
    client.post(url_for('auth.login'), data={ # Login
        "email": "logout@example.com",
        "password": "LogoutPassword123!"
    })

    # Check user_id is in session before logout
    with client.session_transaction() as sess:
        assert 'user_id' in sess

    # 2. Logout
    response = client.post(url_for('auth.logout'), follow_redirects=False)
    assert response.status_code == 302
    assert response.location == url_for('auth.login')

    # Check session is cleared after redirect
    with client.session_transaction() as sess:
        assert 'user_id' not in sess
        assert 'username' not in sess
    
    # Check flashed message on the login page
    redirect_response = client.get(response.location) # Follow redirect
    assert redirect_response.status_code == 200
    assert b"You have been successfully logged out." in redirect_response.data
```
