import pytest
from src.models import hash_password, check_password

def test_hash_password():
    """
    Tests the hash_password function for basic properties.
    """
    sample_password = "mypassword123"
    
    hashed_1 = hash_password(sample_password)
    
    # a. Assert that the returned hash is not None.
    assert hashed_1 is not None
    
    # b. Assert that the returned hash is a string.
    assert isinstance(hashed_1, str)
    
    # c. Assert that the returned hash is different from the original password.
    assert hashed_1 != sample_password
    
    # f. Assert that calling hash_password again with the same sample password 
    #    produces a *different* hash (due to different salts).
    hashed_2 = hash_password(sample_password)
    assert hashed_1 != hashed_2

def test_check_password():
    """
    Tests the check_password function for verifying correct and incorrect passwords.
    """
    sample_password = "securePassword!"
    
    # b. Generates a hash for this password using hash_password.
    hashed_password_str = hash_password(sample_password)
    
    # c. Assert that check_password returns True for the correct password.
    assert check_password(sample_password, hashed_password_str) is True
    
    # d. Assert that check_password returns False for an incorrect password.
    assert check_password("wrongpassword", hashed_password_str) is False
    
    # e. Assert that check_password returns False for a tampered/different hash.
    #    To simulate a "tampered" hash, we can just use a hash of a different password,
    #    or slightly alter the original hash (though direct alteration is less robust).
    #    Using another valid hash from a different password is a good test.
    different_hashed_str = hash_password("anotherpassword")
    assert check_password(sample_password, different_hashed_str) is False

    # Test with an obviously invalid hash string (e.g., too short, wrong format)
    # bcrypt hashes have a specific format, e.g., "$2b$..."
    # An arbitrary string that doesn't match this format should ideally be handled gracefully,
    # though bcrypt.checkpw might raise a ValueError if the salt is invalid.
    # For this test, we'll focus on valid-format but incorrect hashes.
    # If check_password is expected to handle malformed hash strings by returning False,
    # then a specific test for that could be added.
    # For now, we assume validly generated (but incorrect) hashes.
    # Example of a tampered hash (not a valid bcrypt hash, will likely cause error in bcrypt.checkpw):
    # tampered_hash = "not_a_real_hash" 
    # This might raise ValueError: "invalid salt" or similar from bcrypt.checkpw
    # A robust check_password might catch such exceptions and return False.
    # However, the current implementation of check_password directly calls bcrypt.checkpw,
    # so it would propagate the error. We'll stick to logically incorrect but structurally valid hashes.


def test_check_password_with_different_salts():
    """
    Tests that check_password works correctly even if hashes for the same password
    are different due to salting.
    """
    sample_password = "myUniquePassword@2024"
    
    # b. Generates two separate hashes (hash1, hash2) from the same sample password.
    hash1 = hash_password(sample_password)
    hash2 = hash_password(sample_password)
    
    # c. Assert that hash1 and hash2 are different.
    assert hash1 != hash2, "Hashes generated with different salts should not be identical."
    
    # d. Assert that check_password(sample_password, hash1) returns True.
    assert check_password(sample_password, hash1) is True
    
    # e. Assert that check_password(sample_password, hash2) returns True.
    assert check_password(sample_password, hash2) is True
