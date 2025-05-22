from flask import Blueprint, request, jsonify, redirect, url_for, render_template, session, flash
from . import auth_bp  # Assuming auth_bp is defined in src/auth/__init__.py
from src.auth.services import create_user, authenticate_user

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # Render the registration form template
        return render_template('register.html')

    elif request.method == 'POST':
        # Data is already available via request.form in the template
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        form_errors = {}
        if not all([username, email, password, password_confirm]):
            # This specific check might be redundant if UserRegistrationSchema handles all required fields.
            # However, keeping it for explicit "all fields required" type of top-level form error.
            form_errors["form"] = ["All fields are required."] # Ensure error messages are lists
            # flash("All fields are required.", "danger") # Flashing here is optional
            return render_template('register.html', errors=form_errors, request=request), 400

        if password != password_confirm:
            form_errors["password_confirm"] = ["Passwords do not match."]
            return render_template('register.html', errors=form_errors, request=request), 400
        
        # If basic client-side checks pass, proceed to service layer (which uses UserRegistrationSchema)
        result = create_user(username=username, email=email, password=password)

        if result["success"]:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            errors = result.get("errors", {})
            status_code = 400 # Default for validation errors from schema or other logic
            if "database" in errors:
                status_code = 500
                # For database errors, we might not want to expose detailed errors to template
                # flash("Registration failed due to a server issue. Please try again later.", "danger") # Optional flash
                # return render_template('register.html', errors={"form": ["Registration failed due to a server issue."]}, request=request), status_code
            elif errors.get("email") and "Email already registered." in errors["email"]:
                status_code = 409
            
            # errors from UserRegistrationSchema are already in the correct format (dict of lists)
            return render_template('register.html', errors=errors, request=request), status_code

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Pass errors=None or an empty dict if your template expects it
        return render_template('login.html', errors=None) 

    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Basic check for presence of email and password
        if not email or not password:
            flash('Both email and password are required.', 'danger')
            return render_template('login.html', errors={"form": "Both email and password are required."}, email=email), 400

        result = authenticate_user(email=email, password=password)

        if result["success"]:
            session.clear()
            session['user_id'] = result['user']['id']
            session['username'] = result['user']['username'] # Optional, for convenience
            session.permanent = True  # To respect PERMANENT_SESSION_LIFETIME

            flash('Login successful!', 'success')
            # Assuming 'hello' is the endpoint for '/hello' route in app.py
            return redirect(url_for('hello')) 
        else:
            errors = result.get("errors", {})
            # Determine a primary error message to flash
            # The service returns errors in a dict, e.g., {"form": "Invalid..."} or {"email": "Required"}
            # We should flash a user-friendly message.
            if "form" in errors:
                flash_message = errors["form"]
            elif "email" in errors:
                flash_message = errors["email"]
            elif "password" in errors:
                flash_message = errors["password"]
            elif "database" in errors: # Generic message for database errors
                flash_message = "Login failed due to a server issue. Please try again later."
            else:
                flash_message = "Login failed. Please check your credentials."
            
            flash(flash_message, 'danger')
            return render_template('login.html', errors=errors, email=email), 400

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('auth.login'))
