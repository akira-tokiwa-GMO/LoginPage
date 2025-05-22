import os
# import sqlite3 # No longer needed directly in app.py if init_db is fully in core.database
from flask import Flask
from datetime import timedelta # Added for session lifetime

# Import the new centralized init_db function
from src.core.database import init_db as initialize_database_command_func

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Configuration
    # Ensure app.secret_key is set (it's crucial for sessions)
    app.secret_key = os.environ.get('SECRET_KEY', 'dev_default_secret_key') # Use environment variable or a default

    # Configure session lifetime
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=15)

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass # Already exists or error creating it

    # A simple route for testing
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # Import and register blueprints
    # Example: from src.auth import auth_bp
    # app.register_blueprint(auth_bp)
    
    # Import auth blueprint from src.auth (created in a previous task)
    from src.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Import and register the main blueprint
    from src.main import main_bp
    app.register_blueprint(main_bp)

    # Remove the old internal init_db function.
    # The new init_db logic is now in src.core.database.

    @app.cli.command('init-db')
    def init_db_command_cli(): # Renamed for clarity if needed, or keep as init_db_command
        """Initializes the database using the centralized function."""
        try:
            initialize_database_command_func() # This is the imported src.core.database.init_db
            # Logging is now handled within initialize_database_command_func
            # app.logger.info('Database initialization process completed via core.database.init_db.')
        except Exception as e:
            # The init_db in core.database should log its own errors,
            # but we can catch and log here if it re-raises, or for general command failure.
            app.logger.error(f"Failed to initialize database from CLI command: {e}")
            # Optionally, re-raise or exit with error status
            # import sys
            # sys.exit(1)

    return app

if __name__ == '__main__':
    # This allows running the app directly for development
    # In production, a WSGI server like Gunicorn or uWSGI would be used.
    app = create_app()
    app.run(debug=True)
