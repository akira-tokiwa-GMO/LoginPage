# Application Architecture

## 1. Overview
    - Brief description of the project: A web application with user authentication (registration, login, dashboard, logout) using Flask and SQLite.
    - Purpose of this document: To describe the architecture, key components, and design principles of the application.

## 2. Architectural Pattern: Model-View-Controller (MVC)
    - This project loosely follows the Model-View-Controller (MVC) pattern, adapted for a Flask context. The "Controller" aspect is often handled by Flask routes and dedicated service functions.
        - **Model**: Represents data and business logic.
            - `src/models.py`: Contains password hashing utilities (`hash_password`, `check_password` using bcrypt). User data itself is managed via direct SQL interactions coordinated by service functions.
            - `src/core/database.py`: Handles SQLite database connection (`get_db_connection`). The schema initialization logic is within `src/app.py`'s `init_db` command.
        - **View**: Represents the presentation layer (UI).
            - `src/templates/`: Contains Jinja2 HTML templates (`base.html`, `register.html`, `login.html`, `dashboard.html`) that render data dynamically.
            - `src/static/`: Contains static assets like CSS (`style.css`) and client-side JavaScript (`script.js`).
        - **Controller**: Handles user input, interacts with Models and Services, and selects Views for rendering.
            - `src/app.py`: The main application factory (`create_app`) which initializes the Flask app, loads configuration, and registers blueprints.
            - `src/auth/routes.py`: Defines routes for authentication functionalities such as `/register`, `/login`, and `/logout`. These routes delegate business logic to service functions.
            - `src/main/routes.py`: Defines routes for the main application parts, like `/dashboard` and the root index `/`.
            - `src/auth/services.py`: Contains the core business logic for authentication, including user creation (`create_user`) and user authentication (`authenticate_user`). This acts as a service layer between the routes (controllers) and the database/data validation.
            - `src/schemas.py`: Defines data validation schemas.
                - `UserRegistrationSchema`: A Marshmallow-based schema for validating new user registration data, including complex password strength rules.
                - `UserLoginSchema`: A custom class for validating user login credentials (email and password presence/format).

## 3. Key Components
    - **Flask Application (`src/app.py`)**:
        - Implements the application factory pattern (`create_app`).
        - Handles application configuration (e.g., `SECRET_KEY`, `PERMANENT_SESSION_LIFETIME`).
        - Registers blueprints (`auth_bp` from `src.auth`, `main_bp` from `src.main`).
        - Defines a CLI command `flask init-db` for initializing the database schema.
    - **Authentication Blueprint (`src/auth/`)**:
        - Encapsulates all authentication-related functionalities.
        - `__init__.py`: Defines the `auth_bp` blueprint.
        - `routes.py`: Defines HTTP routes and handlers for user registration, login, and logout.
        - `services.py`: Implements the business logic for creating users (including input validation via `UserRegistrationSchema` and password hashing) and authenticating users (including input validation via `UserLoginSchema` and password checking).
    - **Main Blueprint (`src/main/`)**:
        - Handles core application features available after user login.
        - `__init__.py`: Defines the `main_bp` blueprint.
        - `routes.py`: Defines HTTP routes and handlers for the user dashboard (`/dashboard`) and the application's root page (`/`).
    - **Database (`src/core/database.py`, SQLite file `users.db`)**:
        - Utilizes SQLite as the database engine for simplicity and portability.
        - `src/core/database.py` provides a `get_db_connection` utility to connect to the SQLite database. The database file is named `users.db`.
        - WAL (Write-Ahead Logging) mode is typically enabled by default in newer SQLite versions, which improves concurrency and performance.
        - The primary table is `user`, with key fields such as `id` (Primary Key), `username` (Unique, Not Null), `email` (Unique, Not Null), `hashed_password` (Not Null), and timestamps.
    - **Data Schemas/Validation (`src/schemas.py`)**:
        - `UserRegistrationSchema`: A Marshmallow schema used in `src/auth/services.py` to validate the data provided during user registration (username, email, password, password confirmation). It includes comprehensive rules for password strength.
        - `UserLoginSchema`: A custom Python class used in `src/auth/services.py` to validate the email and password fields provided during login.
    - **Password Management (`src/models.py`)**:
        - Uses `bcrypt` library for robust password hashing.
        - `hash_password(password)`: Generates a bcrypt hash for a given password.
        - `check_password(password, hashed_password_str)`: Verifies a plain password against a stored bcrypt hash.

## 4. Directory Structure
    - **`src/`**: Contains all the core application source code.
        - **`auth/`**: Authentication-related blueprint (routes, services).
        - **`main/`**: Main application logic blueprint (routes for dashboard, etc.).
        - **`core/`**: Core utilities like database connection setup.
        - **`static/`**: Static files (CSS, JavaScript, images).
        - **`templates/`**: HTML templates (Jinja2).
        - **`app.py`**: Flask application factory.
        - **`models.py`**: Password hashing utilities (and potentially ORM models in other projects).
        - **`schemas.py`**: Data validation schemas.
    - **`tests/`**: Contains all tests.
        - **`unit/`**: Unit tests for individual components (e.g., models, schemas, services).
        - **`integration/`**: Integration tests for application routes and overall behavior.
        - **`conftest.py`**: Pytest configuration and shared fixtures.
    - **`docs/`**: Project documentation files (like this one, `setup.md`).
    - **`.github/`**: Contains GitHub-specific files.
        - **`workflows/`**: GitHub Actions CI workflow definitions (e.g., `main.yml`).
    - **`instance/`**: This folder is created by Flask when `instance_relative_config=True`. It's designed to hold instance-specific files not meant for version control, such as configuration files and the SQLite database file (`users.db`). It is gitignored.
    - **`venv/`**: (Typically gitignored) Virtual environment directory.
    - **`requirements.txt`**: Project dependencies.
    - **`.flaskenv`**: (Typically gitignored) Environment variables for Flask CLI.

## 5. Technology Stack
    - **Python**: Version 3.9+
    - **Flask**: Core web framework for building the application.
    - **SQLite**: File-based relational database engine.
    - **bcrypt**: Library for password hashing.
    - **Marshmallow**: Library for data validation and serialization (used for `UserRegistrationSchema`).
    - **Jinja2**: Templating engine used by Flask for rendering HTML.
    - **Pytest**: Framework for writing and running unit and integration tests.
    - **pytest-cov**: Pytest plugin for measuring code coverage.
    - **Flake8**: Linter for enforcing Python code style (PEP 8) and detecting errors.
    - **Black**: Code formatter for ensuring consistent Python code style.
    - **isort**: Tool for sorting Python imports automatically.
    - **GitHub Actions**: CI/CD platform for automating builds, tests, and deployments.
    - **HTML/CSS/JavaScript**: Frontend technologies for user interface and interaction.

## 6. Data Flow Examples

    - **User Registration**:
        1. User submits registration form (POST request to `/auth/register`).
        2. `auth.routes.register()` receives the request.
        3. Route calls `auth.services.create_user()` with form data.
        4. `create_user()` instantiates `UserRegistrationSchema` to validate data.
            - If validation fails, errors are returned to the route, which responds with a JSON error.
        5. If validation succeeds, `create_user()` hashes the password using `models.hash_password()`.
        6. `create_user()` connects to the database (`core.database.get_db_connection()`).
        7. It checks if the email already exists (SELECT query).
            - If email exists, an error is returned.
        8. If email is unique, it inserts the new user (username, email, hashed password) into the `user` table (INSERT query).
        9. The service returns a success or failure dictionary to the route.
        10. The route responds with JSON (e.g., success message and user ID, or error details).

    - **User Login**:
        1. User submits login form (POST request to `/auth/login`).
        2. `auth.routes.login()` receives the request.
        3. Route calls `auth.services.authenticate_user()` with form data (email, password).
        4. `authenticate_user()` instantiates `UserLoginSchema` to validate input presence/basic format.
            - If validation fails, errors are returned to the route.
        5. If validation succeeds, `authenticate_user()` connects to the database.
        6. It fetches the user by email (SELECT query).
            - If user not found, an error is returned.
        7. If user found, it calls `models.check_password()` to compare the provided password with the stored hash.
            - If passwords don't match, an error is returned.
        8. If passwords match, user details are stored in the `session`.
        9. The service returns a success or failure dictionary to the route.
        10. The route:
            - If successful, flashes a success message and redirects to the dashboard (or `/hello` as per current implementation).
            - If failed, flashes an error message and re-renders the login page with errors.
```
