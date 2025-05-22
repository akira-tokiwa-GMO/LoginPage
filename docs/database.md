# Database Documentation

## 1. Overview
    - Database Engine: SQLite
    - Database File Name: `app_database.db`
    - Location: `instance/` folder (relative to the project root, e.g., `<project-root>/instance/app_database.db`). This folder is automatically managed by Flask when `instance_relative_config=True` is used in `src/app.py`.
    - Purpose: Stores user credentials (username, email, hashed password) and related application data.

## 2. Schema Definition
    - The primary table in the database is the `user` table.
    - **User Table (`user`)**:
        - The `CREATE TABLE` statement and the `updated_at` trigger are defined and executed by the `init_db` function in `src/core/database.py`, which is called by the `flask init-db` command.
          ```sql
          CREATE TABLE IF NOT EXISTS user (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL, 
              email TEXT NOT NULL UNIQUE,
              password_hash TEXT NOT NULL,
              created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
              updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
          );
          ```
        - The following trigger is also created to automatically update the `updated_at` field:
          ```sql
          CREATE TRIGGER IF NOT EXISTS update_user_updated_at
          AFTER UPDATE ON user
          FOR EACH ROW
          BEGIN
              UPDATE user SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
          END;
          ```
        - **Column Descriptions**:
            - `id`: INTEGER, PRIMARY KEY, AUTOINCREMENT - Unique numerical identifier for each user.
            - `username`: TEXT, NOT NULL - The user's chosen display name. Length constraints (e.g., min 1, max 50) and uniqueness are enforced at the application level by the `UserRegistrationSchema` in `src/schemas.py`, not directly by SQL constraints in the current database schema.
            - `email`: TEXT, NOT NULL, UNIQUE - The user's email address, used for login and communication. The `UNIQUE` constraint ensures no two users can register with the same email.
            - `password_hash`: TEXT, NOT NULL - Stores the bcrypt hash of the user's password for security. (This was previously `hashed_password`).
            - `created_at`: DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP - Timestamp automatically set to when the user record was created.
            - `updated_at`: DATETIME, NOT NULL, DEFAULT CURRENT_TIMESTAMP - Timestamp indicating the last update to the user record. It is automatically updated by the `update_user_updated_at` trigger when a row in the `user` table is updated.

## 3. Write-Ahead Logging (WAL) Mode
    - Explanation: Write-Ahead Logging (WAL) is an alternative to the traditional rollback journal used by SQLite. In WAL mode, changes are written to a separate WAL file before being committed to the main database file.
    - Benefits: WAL mode generally allows for better concurrency (multiple readers can continue reading while a writer is writing) and can offer performance improvements for applications with mixed read/write workloads.
    - How it's enabled: WAL mode is explicitly enabled by the `enable_wal_mode(conn)` function within `src/core/database.py` during the `init_db` process. This function executes `PRAGMA journal_mode = WAL;` and verifies its application.

## 4. Indexing Strategy
    - `email` column: A UNIQUE index is automatically created on this column due to the `UNIQUE` constraint in the `CREATE TABLE` statement. This index is crucial for:
        - Fast lookups of user records by email, especially during login (`authenticate_user` service).
        - Efficiently enforcing the uniqueness of email addresses during registration.
    - `username` column: This column does not have a `UNIQUE` constraint at the database level in the current schema. While unique usernames are enforced at the application level (if required by business logic, e.g., via `UserRegistrationSchema`), the database itself does not enforce this. If frequent lookups by username were required and uniqueness was a strict database-level requirement, an index (and potentially a `UNIQUE` constraint) could be added.
    - `id` column (Primary Key): An index is automatically created for the primary key, ensuring fast lookups by user ID.
    - Other potential indexes: For future consideration, if query patterns evolve (e.g., searching users by `created_at` date ranges), additional indexes might be beneficial.

## 5. Backup and Restore Procedures
    - **Backup**:
        - Method: SQLite databases are single files, so backup is typically a direct file copy of `instance/app_database.db`.
        - Recommendation: Perform backups when the application has minimal write activity. If live backups are necessary, ensure the copy mechanism correctly handles file locks or use SQLite's online backup API (though this is more complex).
        - Frequency: Depends on data criticality and change rate (e.g., daily for active applications).
        - Example command (Linux/macOS):
          ```bash
          cp instance/app_database.db /path/to/your/backup_location/app_database_backup_$(date +%Y%m%d%H%M%S).db
          ```
        - Example command (Windows):
          ```bat
          copy instance\app_database.db C:\path\to\your\backup_location\app_database_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%.db
          ```
    - **Restore**:
        - Method: Replace the existing (or missing/corrupted) `instance/app_database.db` file with a backup copy.
        - Important: The Flask application should be stopped before restoring the database file to prevent connection issues or data corruption.
        - Steps:
            1. Stop the Flask application.
            2. If present, rename or delete the current `instance/app_database.db` file.
            3. Copy the chosen backup file to the `instance/` directory and name it `app_database.db`.
            4. Restart the Flask application.
    - **Testing Restores**: It is crucial to periodically test the restore procedure on a staging or development environment to ensure backups are valid and the process works as expected.

## 6. Database Initialization
    - How the database is created and schema is applied:
        - The database file (`instance/app_database.db`) and its schema (including tables and triggers) are created by running the custom Flask CLI command:
          ```bash
          flask init-db
          ```
        - This command, defined in `src/app.py`, now calls the centralized `init_db()` function in `src/core/database.py`. This function handles database connection, enables WAL mode, and executes the `CREATE TABLE` and `CREATE TRIGGER` statements.

This documentation provides an overview of the database setup, schema, and operational considerations for the application.
```
