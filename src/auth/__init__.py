from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Import routes to ensure they are registered with the blueprint
# This is a common pattern, but be mindful of circular imports
from . import routes
