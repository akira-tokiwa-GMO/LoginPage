from flask import render_template, session, redirect, url_for, flash
from . import main_bp  # Import the blueprint from the current package (src/main)

@main_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access this page.", 'danger')
        return redirect(url_for('auth.login'))
    
    # Retrieve username from session, providing a default if it's not set
    username = session.get('username', 'User') 
    
    # Render the dashboard template, passing the username
    # The template 'dashboard.html' will be created in a subsequent task.
    return render_template('dashboard.html', username=username)

# Optional: Add a simple root route if desired, for example, redirecting to login or dashboard
# @main_bp.route('/')
# def index():
#     if 'user_id' in session:
#         return redirect(url_for('main.dashboard'))
#     return redirect(url_for('auth.login'))
