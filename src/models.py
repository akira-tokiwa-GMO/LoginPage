import bcrypt

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(password: str, hashed_password_str: str) -> bool:
    """Checks if the provided password matches the stored hashed password."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password_str.encode('utf-8'))

# The User model is not strictly necessary for this task,
# but it's good practice to have it.
# class User:
#     id: int
#     username: str
#     email: str
#     hashed_password: str
#     created_at: str
#     updated_at: str
