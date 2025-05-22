import sqlite3
from src.schemas import UserRegistrationSchema, UserLoginSchema
from src.models import hash_password, check_password
from src.core.database import get_db_connection

def create_user(username, email, password):
    schema = UserRegistrationSchema()
    errors = schema.validate({"username": username, "email": email, "password": password})
    if errors:
        return {"success": False, "errors": errors}

    hashed_password_str = hash_password(password)
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            return {"success": False, "errors": {"email": "Email already registered."}}

        # Insert new user
        cursor.execute(
            "INSERT INTO user (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, hashed_password_str)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {"success": True, "user_id": user_id}

    except sqlite3.Error as e:
        # Log the error e if you have a logging mechanism
        return {"success": False, "errors": {"database": "A database error occurred."}}
    finally:
        if conn:
            conn.close()

def authenticate_user(email, password):
    # Validate input using UserLoginSchema
    schema = UserLoginSchema(email=email, password=password)
    if not schema.validate():
        return {"success": False, "errors": schema.errors}

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch user by email
        # The password column in the db is named 'password_hash'
        # And the user table has 'id', 'username', 'email', 'password_hash'
        cursor.execute("SELECT id, username, email, password_hash FROM user WHERE email = ?", (email,))
        user_data = cursor.fetchone()

        if not user_data:
            return {"success": False, "errors": {"form": "Invalid email or password."}}

        # Verify password
        # user_data is a sqlite3.Row object, access columns by index or name
        stored_hashed_password = user_data["password_hash"] 
        if check_password(password, stored_hashed_password):
            # Passwords match
            return {
                "success": True,
                "user": {
                    "id": user_data["id"],
                    "username": user_data["username"],
                    "email": user_data["email"]
                }
            }
        else:
            # Passwords do not match
            return {"success": False, "errors": {"form": "Invalid email or password."}}

    except sqlite3.Error as e:
        # Log the error e if you have a logging mechanism
        # print(f"Database error: {e}") # For debugging
        return {"success": False, "errors": {"database": "A database error occurred."}}
    finally:
        if conn:
            conn.close()
