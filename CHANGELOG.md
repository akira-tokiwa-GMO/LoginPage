# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Standardized database initialization logic in `src/core/database.py`.
  - Database file now consistently `app_database.db` located in the `instance` folder.
  - Ensured explicit WAL mode enabling.
  - Ensured `updated_at` trigger for the `user` table is active.
- Corrected password hash column name usage in `src/auth/services.py` to `password_hash`.
- Modified `/auth/register` POST route to render HTML with errors instead of JSON for improved user experience.
- Updated all relevant documentation (`docs/database.md`, `docs/setup.md`, `README.md`) to reflect these database changes.

### Fixed
- Resolved discrepancies between documented database setup and actual implementation.

### Added
- (List new features added since the last release)

### Deprecated
- (List features once stable that are now deprecated)

### Removed
- (List features removed)

### Security
- (List vulnerabilities addressed)

## [0.1.0] - YYYY-MM-DD
### Added
- Initial release of the Flask Authentication App.
- User registration with email, username, and password (hashed using bcrypt).
- Comprehensive password strength validation (length, uppercase, lowercase, digit, special character) and password confirmation during registration using Marshmallow.
- User login with email and password, validated by a custom schema.
- Session management with a configurable 15-minute permanent session lifetime.
- Protected dashboard page (`/dashboard`) displaying a welcome message to the logged-in user.
- Logout functionality to clear the user session.
- Client-side password strength meter on the registration page.
- Basic project structure including `src/` (with `auth` and `main` blueprints, services, models, schemas), `tests/` (unit and integration), `docs/`, and `.github/workflows/`.
- Unit tests for models (password hashing/checking) and schemas (registration and login validation).
- Integration tests for authentication routes (register, login, logout) and main application routes (dashboard, index redirect).
- GitHub Actions CI workflow (`main.yml`) including steps for:
    - Code checkout.
    - Python setup (3.9).
    - Pip dependency caching.
    - Dependency installation (including dev tools like `pytest`, `flake8`, `black`, `isort`).
    - Linting with Flake8.
    - Formatting checks with Black and isort.
    - Running tests with Pytest and generating code coverage reports (XML and terminal).
    - Uploading coverage reports as build artifacts.
- Initial project documentation:
    - `docs/setup.md`: Detailed development setup guide.
    - `docs/architecture.md`: Overview of the application architecture, components, and data flow.
    - `docs/database.md`: Information on the SQLite database schema, indexing, and backup/restore procedures.
- Root `README.md` providing a user-focused project overview, feature list, quick start guide, and links to other documentation.
- `CONTRIBUTING.md` outlining guidelines for contributing to the project.
- This `CHANGELOG.md` file to track project changes.
```
