from marshmallow import Schema, fields, validate, ValidationError, validates, validates_schema
import re

class UserRegistrationSchema(Schema):
    username = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=50, error="Username must be between 1 and 50 characters.")
    )
    email = fields.Email(required=True)
    password = fields.Str(required=True) # Length and content validated by custom method
    password_confirm = fields.Str(required=True, load_only=True) # Not included in dumped output

    @validates('password')
    def validate_password_strength(self, value):
        errors = []
        if len(value) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", value):
            errors.append("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            errors.append("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", value):
            errors.append("Password must contain at least one digit.")
        if not re.search(r"[\W_]", value): # \W matches non-alphanumeric, _ is often included
            errors.append("Password must contain at least one special character.")
        
        if errors:
            raise ValidationError(errors)

    @validates_schema
    def validate_passwords_match(self, data, **kwargs):
        """
        Ensures that password and password_confirm match.
        password_confirm is already marked as load_only=True, so it won't
        be in the final output data after deserialization and validation.
        """
        if data.get('password') != data.get('password_confirm'):
            # Marshmallow attaches this error to the 'password_confirm' field if specified,
            # or as a general schema error if field_name is not provided or is '_schema'.
            # For fields marked load_only, errors might not always be directly tied if the field
            # isn't expected in output, but it's good practice.
            raise ValidationError("Passwords do not match.", field_name="password_confirm")
        
        # No need to explicitly delete data['password_confirm'] here if it's load_only=True.
        # Marshmallow handles not dumping load_only fields.
        # If it were not load_only, one might do:
        # if 'password_confirm' in data:
        #     del data['password_confirm']

class UserLoginSchema:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.errors = {}

    def _validate_email(self):
        if not self.email:
            self.errors["email"] = "Email is required."
        # Basic email regex: one or more characters, then @, then one or more characters, then ., then one or more characters
        elif not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", self.email):
            self.errors["email"] = "Invalid email format."

    def _validate_password(self):
        if not self.password:
            self.errors["password"] = "Password is required."
        # Optional: Add other password validation rules if needed for login,
        # e.g., minimum length, though usually this is more for registration.
        # For login, the main check is if it matches the stored hash.

    def validate(self):
        self.errors = {} # Reset errors before validation
        self._validate_email()
        self._validate_password()
        return not self.errors
