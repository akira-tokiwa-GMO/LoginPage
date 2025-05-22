import pytest
import os
import tempfile
import shutil # For removing the temp directory if TemporaryDirectory context manager isn't used for everything
from flask import Flask

# Assuming create_app is in src.app
from src.app import create_app 
# The init_db function in my src/app.py is defined inside create_app and exposed via CLI.
# So, I don't import init_db directly from src.core.database as per the original prompt,
# as my current structure differs. I'll use the CLI runner.

@pytest.fixture(scope='function') # Function scope for clean DB per test
def app():
    # Create a temporary directory that will serve as the instance folder
    # tempfile.TemporaryDirectory() automatically handles cleanup on exit.
    temp_instance_dir = tempfile.TemporaryDirectory()
    
    # Define test configuration
    # The database will be created inside temp_instance_dir by init_db
    test_config = {
        "TESTING": True,
        "SECRET_KEY": "test_secret_key_for_pytest_sessions",
        "WTF_CSRF_ENABLED": False, # Common for testing, though not used yet in this project
        # Override the instance path to our temporary directory.
        # Flask's create_app uses app.instance_path, and the init_db in my app.py
        # places users.db inside app.instance_path.
        "INSTANCE_PATH_OVERRIDE": temp_instance_dir.name 
    }

    # Create the Flask app instance with test configuration
    # The create_app function needs to be adapted to accept INSTANCE_PATH_OVERRIDE
    # Or, more simply, if create_app uses instance_relative_config=True,
    # we can rely on Flask finding the instance_path.
    # My current create_app in src/app.py takes instance_relative_config=True.
    # Forcing instance_path is more robust for tests.
    
    # Modification needed in src/app.py to handle INSTANCE_PATH_OVERRIDE, or this won't work directly.
    # A simpler way if create_app is structured for it:
    # app = create_app(test_config, instance_path=temp_instance_dir.name)
    # My current create_app in src/app.py does not accept instance_path as a parameter.
    # I will need to modify create_app to allow instance_path override for tests.
    # For now, I will assume create_app can be modified or a different strategy is used.
    # Let's assume for now create_app is modified as:
    # def create_app(test_config=None, instance_path=None):
    #     app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)
    #     ...
    # Or, if create_app uses os.environ.get for instance_path, we can mock os.environ.
    
    # Given the current create_app structure:
    # app = Flask(__name__, instance_relative_config=True)
    # app.instance_path is determined by Flask.
    # The init_db in my app.py uses app.instance_path.
    # To make this work without modifying create_app, I'll use a monkeypatch for app.instance_path.
    
    flask_app = create_app(test_config)
    
    # Monkeypatch instance_path for this app instance
    # This is a bit of a workaround. Ideally, create_app would allow instance_path injection.
    flask_app.instance_path = temp_instance_dir.name
    
    # Ensure the (temporary) instance folder exists, as Flask might not create it
    # if overridden this way after app creation.
    try:
        os.makedirs(flask_app.instance_path, exist_ok=True)
    except OSError:
        pass


    # Initialize the database within the app context
    with flask_app.app_context():
        # Use the CLI runner to initialize the database.
        # This assumes 'init-db' command is registered on the app.
        runner = flask_app.test_cli_runner()
        result = runner.invoke(args=['init-db'])
        if result.exit_code != 0:
            # Print output if init-db command failed, to help debug
            print("Error during init-db:", result.output) 
            raise RuntimeError("Failed to initialize test database via CLI command.")

    yield flask_app

    # Teardown: TemporaryDirectory context manager handles directory removal.
    # If not using TemporaryDirectory, manual cleanup:
    # shutil.rmtree(db_fd)
    # os.close(db_fd)
    # os.unlink(db_path)
    temp_instance_dir.cleanup()


@pytest.fixture(scope='function')
def client(app: Flask):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app: Flask):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

# Optional: Fixture to provide direct db access if needed for some tests
# @pytest.fixture(scope='function')
# def db(app: Flask):
#     # This would need to connect to the app's configured database
#     # For sqlite, it would be os.path.join(app.instance_path, 'users.db')
#     db_path = os.path.join(app.instance_path, 'users.db')
#     conn = sqlite3.connect(db_path)
#     yield conn
#     conn.close()
```
