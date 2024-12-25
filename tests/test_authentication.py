import pytest
import uuid
from enum import Enum
from functools import partial
from tests.requests_builder import http_request


class AuthenticationEndpoints(Enum):
    REGISTER = ("POST", "http://127.0.0.1:8000/register", "REGISTER USER")
    LOGIN = ("POST", "http://127.0.0.1:8000/login?username={username}&password={password}", "LOGIN USER")

    def __init__(self, request_type, path, switcher):
        self.request_type = request_type
        self.path = path
        self.switcher = switcher


class AuthenticationController:
    def authentication_request_controller(self, key, headers, request_body=None, **kwargs):
        switcher = {
            AuthenticationEndpoints.REGISTER.switcher: partial(
                http_request,
                AuthenticationEndpoints.REGISTER.request_type,
                AuthenticationEndpoints.REGISTER.path,
                headers, request_body, None
            ),
            AuthenticationEndpoints.LOGIN.switcher: partial(
                http_request,
                AuthenticationEndpoints.LOGIN.request_type,
                AuthenticationEndpoints.LOGIN.path.format(username=kwargs.get("username"),
                                                          password=kwargs.get("password")),
                headers, None, None
            )
        }
        if key in switcher:
            return switcher[key]()
        else:
            raise ValueError(f"Invalid key: {key}")


STATUS_CODE_BAD_REQUEST = 400
STATUS_CODE_SUCCESS = 200

DETAILS = {
    "USERNAME_TOO_SHORT": "Username must be between 3 and 30 characters",
    "USERNAME_TOO_LONG": "Username must be between 3 and 30 characters",
    "USERNAME_INVALID_CHARACTERS": "Username can only contain letters, numbers, and underscores",
    "EMAIL_INVALID_FORMAT": "Invalid email address",
    "PASSWORD_TOO_SHORT": "Password must be at least 8 characters long",
    "PASSWORD_MISSING_UPPERCASE": "Password must contain at least one uppercase letter",
    "PASSWORD_MISSING_LOWERCASE": "Password must contain at least one lowercase letter",
    "PASSWORD_MISSING_DIGIT": "Password must contain at least one digit",
    "PASSWORD_MISSING_SPECIAL": "Password must contain at least one special character",
}


class TestRegisterEndpoint:
    @pytest.fixture
    def controller(self):
        return AuthenticationController()

    @pytest.fixture
    def valid_headers(self):
        return {
            "accept": "application/json",
            "Content-Type": "application/json",
        }

    @pytest.fixture
    def generate_unique_user(self):
        """Fixture to generate a unique user."""
        def _generate():
            unique_suffix = str(uuid.uuid4())[:8]
            return {
                "username": f"user_{unique_suffix}",
                "email": f"user_{unique_suffix}@example.com",
                "password": "ValidPassword1!"
            }
        return _generate

    def test_register_username_too_short(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["username"] = "1"  # Invalid username
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["USERNAME_TOO_SHORT"]

    def test_register_username_too_long(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["username"] = "a" * 31  # Invalid username
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["USERNAME_TOO_LONG"]

    def test_register_username_invalid_characters(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["username"] = "invalid@name"  # Invalid username
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["USERNAME_INVALID_CHARACTERS"]

    def test_register_email_invalid_format(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["email"] = "invalid-email"  # Invalid email
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["EMAIL_INVALID_FORMAT"]

    def test_register_password_too_short(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["password"] = "Short1!"  # Invalid password
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["PASSWORD_TOO_SHORT"]

    def test_register_password_missing_uppercase(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["password"] = "lowercase1!"  # Invalid password
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["PASSWORD_MISSING_UPPERCASE"]

    def test_register_password_missing_lowercase(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["password"] = "UPPERCASE1!"  # Invalid password
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["PASSWORD_MISSING_LOWERCASE"]

    def test_register_password_missing_digit(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["password"] = "NoDigit!"  # Invalid password
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["PASSWORD_MISSING_DIGIT"]

    def test_register_password_missing_special_character(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["password"] = "ValidPass1"  # Invalid password
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["PASSWORD_MISSING_SPECIAL"]

    def test_register_success(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()  # Unique user
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_SUCCESS
        assert response.json()["username"] == user_data["username"]
        assert response.json()["email"] == user_data["email"]
