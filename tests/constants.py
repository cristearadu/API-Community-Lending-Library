from enum import Enum
from typing import Callable, List


class StatusCode(Enum):
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403


class ErrorDetail(Enum):
    ADMIN_REGISTRATION_FORBIDDEN = "Cannot register as admin"
    EMAIL_ALREADY_EXISTS = "Email already registered"
    EMAIL_DOMAIN_TOO_LONG = "Email domain cannot exceed 255 characters"
    EMAIL_INVALID_FORMAT = "Invalid email address"
    EMAIL_LOCAL_PART_TOO_LONG = "Email local part cannot exceed 64 characters"
    EMAIL_TOO_LONG = "Total email length cannot exceed 254 characters"
    FIELD_REQUIRED = "Field '{}' is required"
    INVALID_CREDENTIALS = "Incorrect username or password"
    INVALID_PASSWORD = "Invalid password"
    INVALID_ROLE = "Invalid role"
    NOT_AUTHENTICATED = "Not authenticated"
    PASSWORD_EMPTY = "Password cannot be empty"
    PASSWORD_MISSING_DIGIT = "Password must contain at least one digit"
    PASSWORD_MISSING_LOWERCASE = "Password must contain at least one lowercase letter"
    PASSWORD_MISSING_SPECIAL = "Password must contain at least one special character"
    PASSWORD_MISSING_UPPERCASE = "Password must contain at least one uppercase letter"
    PASSWORD_TOO_SHORT = "Password must be at least 8 characters long"
    TOKEN_EXPIRED = "Could not validate credentials"
    TOKEN_INVALID = "Could not validate credentials"
    USERNAME_ALREADY_EXISTS = "Username already registered"
    USERNAME_EMPTY = "Username cannot be empty"
    USERNAME_INVALID_CHARACTERS = (
        "Username can only contain letters, numbers, and underscores"
    )
    USERNAME_TOO_LONG = "Username must be between 3 and 30 characters"
    USERNAME_TOO_SHORT = "Username must be between 3 and 30 characters"
    USER_NOT_FOUND = "User not found"


class TestData(Enum):
    # Valid test data
    VALID_PASSWORD = "ValidP@ss1"

    # Invalid password patterns
    INVALID_PASSWORD_SHORT = "short"
    INVALID_PASSWORD_NO_UPPER = "nouppercase123"
    INVALID_PASSWORD_NO_LOWER = "NOLOWERCASE123"
    INVALID_PASSWORD_NO_SPECIAL = "NoSpecial123"
    INVALID_PASSWORD_NO_NUMBERS = "No@Numbers"
    INVALID_PASSWORD_SHORT_WITH_REQS = "Ab@1"

    # Wrong passwords for testing
    WRONG_PASSWORD = "WrongPassword123!"
    WRONG_PASSWORD_VARIANT = "WrongP@ss1"

    # Username patterns with placeholders
    USERNAME_LETTERS_NUMBERS = "usr{}"
    USERNAME_NUMBERS_FIRST = "123{}"
    USERNAME_WITH_UNDERSCORE = "usr_{}"
    USERNAME_UPPERCASE = "ABC{}"
    USERNAME_LOWERCASE = "low{}"

    # Invalid username patterns
    INVALID_USERNAME_TOO_SHORT = "ab"
    INVALID_USERNAME_TOO_LONG = "a" * 31
    INVALID_USERNAME_SPECIAL_CHARS = "user@name"
    INVALID_USERNAME_SPACES = "user name"

    # Email patterns
    EMAIL_STANDARD = "test_{}@example.com"
    EMAIL_ALTERNATIVE = "user_{}@test.com"
    VALID_EMAIL_PATTERN = "test_{}@example.com"

    # Common patterns
    RANDOM_SUFFIX = "{}"
    TEST_PREFIX = "test_{}"
    USER_PREFIX = "user_{}"
    USERNAME_PATTERN = "user_{}"
    EMAIL_PATTERN = "user_{}@example.com"

    # Unicode test patterns
    CHINESE_USERNAME = "参鸔廊摉"
    BULGARIAN_USERNAME = "ьАьпЯ"
    ARABIC_USERNAME = "كمفثش"
    KOREAN_USERNAME = "좿힩낧엑되뱀꾂"

    # Role test data
    ROLE_BUYER = "buyer"
    ROLE_ADMIN = "admin"
    ROLE_INVALID = "invalid_role"
    ROLE_EMPTY = ""
    ROLE_NUMERIC = "123"
    ROLE_SPECIAL_CHARS = "buyer@123"

    # Test email addresses
    TEST_EMAIL = "test@example.com"
    TEST_USERNAME = "testuser"
    TEST_USERNAME_ALT = "user123"
    EMPTY_STRING = ""
    WHITESPACE_STRING = "   "

    # Field names for error messages
    FIELD_USERNAME = "username"
    FIELD_EMAIL = "email"
    FIELD_PASSWORD = "password"

    # Token test data
    INVALID_TOKEN = "not_a_token"
    BEARER_NO_TOKEN = "Bearer"
    BEARER_EMPTY_TOKEN = "Bearer "
    INVALID_JWT = "Bearer invalid.token.format"
    WRONG_PREFIX_TOKEN = "Token valid_token"
    EMPTY_TOKEN = ""

    # Malformed token patterns
    MALFORMED_JWT = "Bearer not.a.token"
    LONG_TOKEN = "Bearer " + "a" * 100
    EXTRA_DOTS_TOKEN = "Bearer token.with.two.dots.only"
    SINGLE_PART_TOKEN = "Bearer token"

    # Test usernames
    NONEXISTENT_USER = "nonexistent_user"


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


class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"
