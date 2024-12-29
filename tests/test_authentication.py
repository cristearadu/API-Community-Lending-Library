import pytest
import uuid
from enum import Enum
from functools import partial
from tests.requests_builder import http_request
import time
from tests.utils import decode_token_payload


class AuthenticationEndpoints(Enum):
    REGISTER = ("POST", "http://127.0.0.1:8000/register", "REGISTER USER")
    LOGIN = ("POST", "http://127.0.0.1:8000/login", "LOGIN USER")
    ME = ("GET", "http://127.0.0.1:8000/users/me", "GET CURRENT USER")

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
                AuthenticationEndpoints.LOGIN.path,
                headers, 
                {"username": kwargs.get("username"), "password": kwargs.get("password")},
                None
            ),
            AuthenticationEndpoints.ME.switcher: partial(
                http_request,
                AuthenticationEndpoints.ME.request_type,
                AuthenticationEndpoints.ME.path,
                headers, None, None
            )
        }
        if key in switcher:
            return switcher[key]()
        else:
            raise ValueError(f"Invalid key: {key}")


STATUS_CODE_BAD_REQUEST = 400
STATUS_CODE_SUCCESS = 200
STATUS_CODE_UNAUTHORIZED = 401
STATUS_CODE_FORBIDDEN = 403

DETAILS = {
    "USERNAME_ALREADY_EXISTS": "Username already registered",
    "EMAIL_ALREADY_EXISTS": "Email already registered",
    "USERNAME_TOO_SHORT": "Username must be between 3 and 30 characters",
    "USERNAME_TOO_LONG": "Username must be between 3 and 30 characters",
    "USERNAME_INVALID_CHARACTERS": "Username can only contain letters, numbers, and underscores",
    "EMAIL_INVALID_FORMAT": "Invalid email address",
    "PASSWORD_TOO_SHORT": "Password must be at least 8 characters long",
    "PASSWORD_MISSING_UPPERCASE": "Password must contain at least one uppercase letter",
    "PASSWORD_MISSING_LOWERCASE": "Password must contain at least one lowercase letter",
    "PASSWORD_MISSING_DIGIT": "Password must contain at least one digit",
    "PASSWORD_MISSING_SPECIAL": "Password must contain at least one special character",
    "USERNAME_EMPTY": "Username cannot be empty",
    "PASSWORD_EMPTY": "Password cannot be empty",
    "INVALID_CREDENTIALS": "Incorrect username or password"
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
        user_data["username"] = "1"
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["USERNAME_TOO_SHORT"]

    def test_register_username_too_long(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["username"] = "a" * 31
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["USERNAME_TOO_LONG"]

    def test_register_username_invalid_characters(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["username"] = "invalid@name"
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["USERNAME_INVALID_CHARACTERS"]

    def test_register_email_invalid_format(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["email"] = "invalid-email"
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["EMAIL_INVALID_FORMAT"]

    def test_register_password_too_short(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["password"] = "Short1!"
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["PASSWORD_TOO_SHORT"]

    def test_register_password_missing_uppercase(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["password"] = "lowercase1!"
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["PASSWORD_MISSING_UPPERCASE"]

    def test_register_password_missing_lowercase(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["password"] = "UPPERCASE1!"
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["PASSWORD_MISSING_LOWERCASE"]

    def test_register_password_missing_digit(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["password"] = "NoDigit!"
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["PASSWORD_MISSING_DIGIT"]

    def test_register_password_missing_special_character(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        user_data["password"] = "ValidPass1"
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["PASSWORD_MISSING_SPECIAL"]

    def test_register_success(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_SUCCESS
        assert response.json()["username"] == user_data["username"]
        assert response.json()["email"] == user_data["email"]

    def test_register_duplicate_username(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_SUCCESS

        duplicate_user = generate_unique_user()
        duplicate_user["username"] = user_data["username"]
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=duplicate_user
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == "Username already registered"

    def test_register_duplicate_email(self, controller, valid_headers, generate_unique_user):
        user_data = generate_unique_user()
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data
        )
        assert response.status_code == STATUS_CODE_SUCCESS

        duplicate_user = generate_unique_user()
        duplicate_user["email"] = user_data["email"]
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=duplicate_user
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == "Email already registered"


class TestLoginEndpoint:
    def test_login_success(self, auth_user):
        """Test already covered by auth_user fixture"""
        assert auth_user["token"] is not None
        assert len(auth_user["token"]) > 0
        assert auth_user["token"].count('.') == 2

    def test_login_success_multiple_times(self, controller, valid_headers, auth_user):
        # Get first token from auth_user
        token1 = auth_user["token"]
        
        # Wait 2 seconds to ensure different exp time
        time.sleep(2)
        
        # Get second token
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            username=auth_user["user"]["username"],
            password=auth_user["user"]["password"]
        )
        assert response.status_code == 200
        token2 = response.json()["access_token"]
    
        # Verify tokens are different
        assert token1 != token2
        
        # Compare token payloads
        payload1 = decode_token_payload(token1)
        payload2 = decode_token_payload(token2)
        
        # Verify that only expiration times are different
        assert payload1['sub'] == payload2['sub']  # Same username
        assert payload1['exp'] != payload2['exp']  # Different expiration times

    def test_login_empty_username(self, controller, valid_headers):
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            username="",
            password="anypassword"
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["USERNAME_EMPTY"]

    def test_login_empty_password(self, controller, valid_headers, auth_user):
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            username=auth_user["user"]["username"],
            password=""
        )
        assert response.status_code == STATUS_CODE_BAD_REQUEST
        assert response.json()["detail"] == DETAILS["PASSWORD_EMPTY"]

    def test_login_invalid_username(self, controller, valid_headers):
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            username="nonexistent_user",
            password="ValidPassword1!"
        )
        assert response.status_code == STATUS_CODE_UNAUTHORIZED
        assert response.json()["detail"] == DETAILS["INVALID_CREDENTIALS"]

    def test_login_invalid_password(self, controller, valid_headers, auth_user):
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            username=auth_user["user"]["username"],
            password="WrongPassword1!"
        )
        assert response.status_code == STATUS_CODE_UNAUTHORIZED
        assert response.json()["detail"] == DETAILS["INVALID_CREDENTIALS"]

    def test_login_case_sensitive_username(self, controller, valid_headers, auth_user):
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            username=auth_user["user"]["username"].upper(),
            password=auth_user["user"]["password"]
        )
        assert response.status_code == STATUS_CODE_UNAUTHORIZED
        assert response.json()["detail"] == DETAILS["INVALID_CREDENTIALS"]

    def test_login_success_with_protected_endpoint(self, controller, auth_user):
        # Test protected endpoint
        me_response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.ME.switcher,
            headers=auth_user["headers"]
        )
        assert me_response.status_code == 200
        assert me_response.json()["username"] == auth_user["user"]["username"]
        assert me_response.json()["email"] == auth_user["user"]["email"]

    def test_protected_endpoint_without_token(self, controller, valid_headers):
        """Test that protected endpoint fails without token (Forbidden)"""
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.ME.switcher,
            headers=valid_headers
        )
        assert response.status_code == STATUS_CODE_FORBIDDEN

    def test_protected_endpoint_with_invalid_token(self, controller, valid_headers):
        """Test that protected endpoint fails with invalid token (Unauthorized)"""
        invalid_auth_headers = {
            **valid_headers,
            "Authorization": "Bearer invalid.token.here"
        }
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.ME.switcher,
            headers=invalid_auth_headers
        )
        assert response.status_code == STATUS_CODE_UNAUTHORIZED
