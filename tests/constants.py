from enum import Enum
from typing import Callable, List


class StatusCode(Enum):
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403


class ErrorDetail(Enum):
    USERNAME_ALREADY_EXISTS = "Username already registered"
    EMAIL_ALREADY_EXISTS = "Email already registered"
    USERNAME_TOO_SHORT = "Username must be between 3 and 30 characters"
    USERNAME_TOO_LONG = "Username must be between 3 and 30 characters"
    EMAIL_LOCAL_PART_TOO_LONG = "Email local part cannot exceed 64 characters"
    EMAIL_DOMAIN_TOO_LONG = "Email domain cannot exceed 255 characters"
    EMAIL_TOO_LONG = "Total email length cannot exceed 254 characters"
    USERNAME_INVALID_CHARACTERS = (
        "Username can only contain letters, numbers, and underscores"
    )
    EMAIL_INVALID_FORMAT = "Invalid email address"
    PASSWORD_TOO_SHORT = "Password must be at least 8 characters long"
    PASSWORD_MISSING_UPPERCASE = "Password must contain at least one uppercase letter"
    PASSWORD_MISSING_LOWERCASE = "Password must contain at least one lowercase letter"
    PASSWORD_MISSING_DIGIT = "Password must contain at least one digit"
    PASSWORD_MISSING_SPECIAL = "Password must contain at least one special character"
    USERNAME_EMPTY = "Username cannot be empty"
    PASSWORD_EMPTY = "Password cannot be empty"
    INVALID_CREDENTIALS = "Incorrect username or password"
    TOKEN_EXPIRED = "Could not validate credentials"
    TOKEN_INVALID = "Could not validate credentials"


# Test Data
SPECIAL_CHARACTERS = [
    "<",
    ">",
    '"',
    "'",
    ";",
    "=",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    "|",
    "/",
    "\\",
    "!",
    "@",
    "#",
    "$",
    "%",
    "^",
    "&",
    "*",
]

INVALID_EMAIL_FORMATS: List[Callable[[str], str]] = [
    # Basic format violations
    lambda x: f"notanemail{x}",  # No @ symbol
    lambda x: f"@nodomain{x}.com",  # No local part
    lambda x: f"{x}@",  # No domain
    lambda x: f"@.",  # Just @.
    lambda x: f"{x}@.",  # No domain extension
    # Invalid characters
    lambda x: f"spaces in{x}@domain.com",  # Spaces in local part
    lambda x: f"{x}@dom ain.com",  # Spaces in domain
    lambda x: f"{x}#@domain.com",  # Invalid special char
    lambda x: f"{x}@@domain.com",  # Double @
    # Invalid structure
    lambda x: f"@{x}@domain.com",  # Multiple @ symbols
    lambda x: f"{x}@domain@com",  # @ in wrong place
    lambda x: f"{x}",  # Just text
    lambda x: f"",  # Empty string
    lambda x: f" ",  # Just space
]
