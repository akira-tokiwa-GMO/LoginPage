import pytest
from flask import url_for, session

# --- Test Dashboard Access (/dashboard) ---

def test_dashboard_unauthenticated_access(client):
    """Test GET /dashboard without logging in."""
    response = client.get(url_for('main.dashboard'), follow_redirects=False)
    
    assert response.status_code == 302
    assert response.location == url_for('auth.login')

    # Check for flashed message on the redirected page (login page)
    redirected_response = client.get(response.location)
    assert redirected_response.status_code == 200
    assert b"Please log in to access this page." in redirected_response.data

def test_dashboard_authenticated_access(client):
    """Test GET /dashboard after logging in."""
    # Step 1: Register and Authenticate a user
    username = "dashboard_user"
    email = "dashboard@example.com"
    password = "DashboardPassword123!"

    reg_response = client.post(url_for('auth.register'), data={
        "username": username,
        "email": email,
        "password": password,
        "password_confirm": password
    })
    assert reg_response.status_code == 201 # Assuming registration returns 201 JSON

    login_response = client.post(url_for('auth.login'), data={
        "email": email,
        "password": password
    }, follow_redirects=True) # Follow redirect to wherever login leads (e.g., /hello)
    
    # Ensure login was successful by checking if the session is set
    # (even if it redirects to /hello, session should be set before that)
    with client.session_transaction() as sess:
        assert 'user_id' in sess
        assert sess['username'] == username

    # Step 2: Access Dashboard
    response = client.get(url_for('main.dashboard'))
    
    assert response.status_code == 200
    assert f"Welcome, {username}!".encode('utf-8') in response.data # Check for personalized welcome
    assert b"Logout" in response.data # Check for logout form/button

# --- Test Index/Root Access (/) ---
# These tests assume the optional index route in src/main/routes.py is active.
# If not, these would expect 404.

def test_index_unauthenticated_access(client):
    """Test GET / (index) without logging in."""
    response = client.get(url_for('main.index'), follow_redirects=False) # Assuming endpoint name 'index' for '/'
    
    assert response.status_code == 302
    assert response.location == url_for('auth.login')

def test_index_authenticated_access(client):
    """Test GET / (index) after logging in."""
    # Step 1: Register and Authenticate a user
    username = "index_user"
    email = "index@example.com"
    password = "IndexPassword123!"

    reg_response = client.post(url_for('auth.register'), data={
        "username": username,
        "email": email,
        "password": password,
        "password_confirm": password
    })
    assert reg_response.status_code == 201

    login_response = client.post(url_for('auth.login'), data={
        "email": email,
        "password": password
    }, follow_redirects=True) 
    
    with client.session_transaction() as sess:
        assert 'user_id' in sess

    # Step 2: Access Index
    response = client.get(url_for('main.index'), follow_redirects=False) # Assuming endpoint 'index' for '/'
    
    assert response.status_code == 302
    assert response.location == url_for('main.dashboard')
```
