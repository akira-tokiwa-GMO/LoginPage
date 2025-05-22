import sqlite3
import os
from flask import current_app, g # g might be useful for managing connection per request

DATABASE_NAME = "app_database.db" # As specified

def get_db_connection():
    """
    Connects to the SQLite database.
    The connection is stored in Flask's 'g' object if not already present for the current request context.
    Ensures the instance path exists.
    """
    # Construct database path using current_app.instance_path
    db_path = os.path.join(current_app.instance_path, DATABASE_NAME)

    # Ensure the instance folder exists
    try:
        os.makedirs(current_app.instance_path, exist_ok=True)
    except OSError as e:
        # Handle potential error during directory creation, e.g., permission issues
        current_app.logger.error(f"Error creating instance directory {current_app.instance_path}: {e}")
        raise

    # Using g to store/retrieve connection for the current app context
    # This is a common pattern for managing resources during a request.
    # For CLI commands or init_db, direct connection might also be fine.
    if 'db_conn' not in g:
        try:
            g.db_conn = sqlite3.connect(db_path)
            g.db_conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            current_app.logger.error(f"Database connection error to {db_path}: {e}")
            raise
    return g.db_conn

def close_db_connection(exception=None):
    """Closes the database connection at the end of the request."""
    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()

def enable_wal_mode(conn):
    """Enables Write-Ahead Logging (WAL) mode for the SQLite database."""
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode = WAL;")
        # Verify WAL mode
        result = cursor.fetchone()
        if result and result[0].lower() == "wal":
            current_app.logger.info("WAL mode enabled successfully.")
        else:
            # WAL mode might already be set, or this PRAGMA might not return a mode string on some versions/configs
            # Check current mode if verification fails or is ambiguous
            cursor.execute("PRAGMA journal_mode;")
            current_mode = cursor.fetchone()
            if current_mode and current_mode[0].lower() == "wal":
                 current_app.logger.info(f"WAL mode is active: {current_mode[0]}.")
            else:
                 current_app.logger.warning(f"Failed to verify WAL mode. Current mode: {current_mode[0] if current_mode else 'Unknown'}.")
        cursor.close()
    except sqlite3.Error as e:
        current_app.logger.error(f"Error enabling WAL mode: {e}")

def create_tables(conn):
    """Creates database tables if they don't already exist."""
    try:
        cursor = conn.cursor()
        # User table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT NOT NULL, -- No UNIQUE constraint here by default
          email TEXT NOT NULL UNIQUE,
          password_hash TEXT NOT NULL, -- Changed from hashed_password
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
        current_app.logger.info("User table schema ensured.")

        # Trigger to update 'updated_at' timestamp on user table update
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_user_updated_at
        AFTER UPDATE ON user
        FOR EACH ROW
        BEGIN
            UPDATE user SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
        END;
        """)
        current_app.logger.info("User updated_at trigger ensured.")
        
        conn.commit()
        cursor.close()
    except sqlite3.Error as e:
        current_app.logger.error(f"Error creating tables: {e}")
        # Consider re-raising or handling more gracefully if critical
        raise

def init_db():
    """
    Initializes the database: enables WAL mode and creates tables.
    This function should be called within an application context.
    """
    db_path = os.path.join(current_app.instance_path, DATABASE_NAME)
    current_app.logger.info(f"Initializing database at: {db_path}")
    
    # Get a direct connection for initialization, not necessarily tied to 'g'
    # as this is a one-off setup command.
    conn = None
    try:
        # Ensure instance path exists before connecting
        os.makedirs(current_app.instance_path, exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row # Good practice even for init
        
        enable_wal_mode(conn)
        create_tables(conn)
        
        current_app.logger.info("Database initialization complete.")
    except sqlite3.Error as e:
        current_app.logger.error(f"Failed to initialize database {db_path}: {e}")
        raise # Re-raise to indicate failure of init-db command
    except OSError as e:
        current_app.logger.error(f"OS Error during database initialization (e.g. creating instance path {current_app.instance_path}): {e}")
        raise
    finally:
        if conn:
            conn.close()

# It's common to register close_db_connection with app.teardown_appcontext
# in create_app if using 'g' for connection management during requests.
# def init_app(app):
#     app.teardown_appcontext(close_db_connection)
#     # Any other app-specific DB setup
```
