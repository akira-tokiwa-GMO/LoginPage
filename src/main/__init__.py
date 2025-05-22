from flask import Blueprint

# Define the blueprint for the main part of the application
# No url_prefix means routes defined here will be at the root or as specified in the route
main_bp = Blueprint('main', __name__)

# Import routes to ensure they are registered with the blueprint
# This is a common pattern, but be mindful of circular imports.
# This file (src/main/routes.py) will be created in a subsequent task.
from . import routes
