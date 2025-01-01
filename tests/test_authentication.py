import pytest
import time
from tests.constants import (
    ErrorDetail,
    SPECIAL_CHARACTERS,
    INVALID_EMAIL_FORMATS,
    UserRole,
    TestData,
)
from datetime import datetime, timedelta
from jose import jwt
from config import settings
from tests.controllers import AuthenticationEndpoints
from tests.utils.string_generators import (
    decode_token_payload,
    generate_random_string,
)
from fastapi import status


class TestRegisterEndpoint:
    """Test cases for user registration endpoint."""

    def test_register_success(self, controller, valid_headers, generate_unique_user):
        """Test successful registration."""
        user_data = generate_unique_user()
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not response.content  # Verify empty response body

    def test_register_duplicate_username(
        self, controller, valid_headers, generate_unique_user
    ):
        """Test registration fails with duplicate username."""
        user_data = generate_unique_user()

        # First registration
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Second registration with same username
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == ErrorDetail.USERNAME_ALREADY_EXISTS.value

    def test_register_duplicate_email(self, controller, valid_headers, registered_user):
        """Test registration fails with duplicate email."""
        new_user = {
            "username": f"different_{generate_random_string(8)}",
            "email": registered_user["email"],  # Use existing email
            "password": TestData.VALID_PASSWORD.value,
        }
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=new_user,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == ErrorDetail.EMAIL_ALREADY_EXISTS.value

    def test_register_invalid_username_length(
        self, controller, valid_headers, generate_unique_user
    ):
        """Test registration fails with invalid username length."""
        user_data = generate_unique_user()
        user_data["username"] = generate_random_string(2)  # 2 characters
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == ErrorDetail.USERNAME_TOO_SHORT.value

    def test_register_invalid_email_format(
        self, controller, valid_headers, generate_unique_user
    ):
        """Test registration fails with invalid email format."""
        for idx, email_format in enumerate(INVALID_EMAIL_FORMATS):
            random_suffix = generate_random_string(8)
            user_data = generate_unique_user(f"emailtest{idx}")

            invalid_email = email_format(random_suffix)
            user_data["email"] = invalid_email

            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body=user_data,
            )

            # Debug information
            print(
                f"\nTesting email format: {email_format.__doc__ if email_format.__doc__ else email_format}"
            )
            print(f"Testing email value: {invalid_email}")
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")

            error_msg = (
                f"Email '{invalid_email}' should be invalid but was accepted. "
                f"Status: {response.status_code}, "
                f"Response: {response.text}"
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert (
                response.json()["detail"] == ErrorDetail.EMAIL_INVALID_FORMAT.value
            ), error_msg

    def test_register_invalid_password(self, controller, valid_headers):
        """Test registration with invalid passwords"""
        invalid_passwords = [
            (
                TestData.INVALID_PASSWORD_SHORT.value,
                ErrorDetail.PASSWORD_TOO_SHORT.value,
            ),
            (
                TestData.INVALID_PASSWORD_NO_UPPER.value,
                ErrorDetail.PASSWORD_MISSING_UPPERCASE.value,
            ),
            (
                TestData.INVALID_PASSWORD_NO_LOWER.value,
                ErrorDetail.PASSWORD_MISSING_LOWERCASE.value,
            ),
            (
                TestData.INVALID_PASSWORD_NO_SPECIAL.value,
                ErrorDetail.PASSWORD_MISSING_SPECIAL.value,
            ),
            (
                TestData.INVALID_PASSWORD_NO_NUMBERS.value,
                ErrorDetail.PASSWORD_MISSING_DIGIT.value,
            ),
            (
                TestData.INVALID_PASSWORD_SHORT_WITH_REQS.value,
                ErrorDetail.PASSWORD_TOO_SHORT.value,
            ),
        ]

        for password, expected_error in invalid_passwords:
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body={
                    "username": TestData.USERNAME_PATTERN.value.format(
                        generate_random_string(8)
                    ),
                    "email": TestData.EMAIL_PATTERN.value.format(
                        generate_random_string(8)
                    ),
                    "password": password,
                },
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["detail"] == expected_error

    def test_email_validation(self, controller, valid_headers, generate_unique_user):
        """Test email validations."""
        user_data = generate_unique_user()

        user_data["email"] = f"{'a' * 246}@example.com"  # Creates email > 256 chars
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email local part cannot exceed 64 characters" in response.text

    def test_username_special_cases(self, controller, valid_headers):
        """Test registration with invalid username patterns"""
        test_cases = [
            (
                TestData.INVALID_USERNAME_TOO_SHORT.value,
                ErrorDetail.USERNAME_TOO_SHORT.value,
            ),
            (
                TestData.INVALID_USERNAME_TOO_LONG.value,
                ErrorDetail.USERNAME_TOO_LONG.value,
            ),
            (
                TestData.INVALID_USERNAME_SPECIAL_CHARS.value,
                ErrorDetail.USERNAME_INVALID_CHARACTERS.value,
            ),
            (
                TestData.INVALID_USERNAME_SPACES.value,
                ErrorDetail.USERNAME_INVALID_CHARACTERS.value,
            ),
        ]

        for username, expected_error in test_cases:
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body={
                    "username": username,
                    "email": TestData.VALID_EMAIL_PATTERN.value.format(
                        generate_random_string(8)
                    ),
                    "password": TestData.VALID_PASSWORD.value,
                },
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["detail"] == expected_error

    def test_valid_username_patterns(self, controller, valid_headers):
        """Test registration with various valid username patterns"""
        unique_suffix = generate_random_string(4)

        valid_username_patterns = [
            TestData.USERNAME_LETTERS_NUMBERS.value.format(unique_suffix),
            TestData.USERNAME_NUMBERS_FIRST.value.format(unique_suffix),
            TestData.USERNAME_WITH_UNDERSCORE.value.format(unique_suffix),
            TestData.USERNAME_UPPERCASE.value.format(unique_suffix),
            TestData.USERNAME_LOWERCASE.value.format(unique_suffix),
        ]

        for username in valid_username_patterns:
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body={
                    "username": username,
                    "email": TestData.EMAIL_PATTERN.value.format(
                        generate_random_string(8)
                    ),
                    "password": TestData.VALID_PASSWORD.value,
                },
            )

            assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_default_role(self, controller, valid_headers, generate_unique_user):
        """Test default role when not specified."""
        user_data = generate_unique_user()
        del user_data["role"]

        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Login to verify default role
        login_response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            request_body={
                "username": user_data["username"],
                "password": user_data["password"],
            },
        )
        assert login_response.status_code == status.HTTP_200_OK

        token = login_response.json()["access_token"]
        me_headers = {**valid_headers, "Authorization": f"Bearer {token}"}
        me_response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.ME.switcher,
            headers=me_headers,
        )

        assert me_response.status_code == status.HTTP_200_OK
        assert me_response.json()["role"] == UserRole.BUYER

    def test_role_validation(self, controller, valid_headers):
        """Test that role validation rejects invalid roles"""
        test_cases = [
            # (role, expected_status, expected_error)
            (
                TestData.ROLE_INVALID.value,
                status.HTTP_400_BAD_REQUEST,
                ErrorDetail.INVALID_ROLE.value,
            ),
            (
                TestData.ROLE_EMPTY.value,
                status.HTTP_400_BAD_REQUEST,
                ErrorDetail.INVALID_ROLE.value,
            ),
            (
                TestData.ROLE_NUMERIC.value,
                status.HTTP_400_BAD_REQUEST,
                ErrorDetail.INVALID_ROLE.value,
            ),
            (
                TestData.ROLE_SPECIAL_CHARS.value,
                status.HTTP_400_BAD_REQUEST,
                ErrorDetail.INVALID_ROLE.value,
            ),
            (
                TestData.ROLE_ADMIN.value,
                status.HTTP_403_FORBIDDEN,
                ErrorDetail.ADMIN_REGISTRATION_FORBIDDEN.value,
            ),
        ]

        for role, expected_status, expected_error in test_cases:
            print(f"\nTesting role: {role}")
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body={
                    "username": TestData.USERNAME_PATTERN.value.format(
                        generate_random_string(8)
                    ),
                    "email": TestData.EMAIL_PATTERN.value.format(
                        generate_random_string(8)
                    ),
                    "password": TestData.VALID_PASSWORD.value,
                    "role": role,
                },
            )

            assert response.status_code == expected_status
            assert response.json()["detail"] == expected_error

    def test_registration_missing_fields(self, controller, valid_headers):
        """Test registration with missing fields"""
        test_cases = [
            (
                {},
                ErrorDetail.FIELD_REQUIRED.value.format(TestData.FIELD_USERNAME.value),
            ),  # All fields missing
            (
                {
                    "email": TestData.TEST_EMAIL.value,
                    "password": TestData.VALID_PASSWORD.value,
                },
                ErrorDetail.FIELD_REQUIRED.value.format(TestData.FIELD_USERNAME.value),
            ),
            (
                {
                    "username": TestData.TEST_USERNAME.value,
                    "password": TestData.VALID_PASSWORD.value,
                },
                ErrorDetail.FIELD_REQUIRED.value.format(TestData.FIELD_EMAIL.value),
            ),
            (
                {
                    "username": TestData.TEST_USERNAME.value,
                    "email": TestData.TEST_EMAIL.value,
                },
                ErrorDetail.FIELD_REQUIRED.value.format(TestData.FIELD_PASSWORD.value),
            ),
        ]

        for request_body, expected_error in test_cases:
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body=request_body,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["detail"] == expected_error


class TestLoginEndpoint:
    def test_login_success(self, auth_user):
        """Test successful login returns valid JWT token"""
        assert auth_user["token"] is not None
        assert len(auth_user["token"]) > 0
        assert auth_user["token"].count(".") == 2

    def test_login_success_multiple_times(self, controller, valid_headers, auth_user):
        """Test that multiple logins for the same user generate different tokens"""
        token1 = auth_user["token"]

        time.sleep(2)

        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            request_body={
                "username": auth_user["user"]["username"],
                "password": auth_user["user"]["password"],
            },
        )
        assert response.status_code == status.HTTP_200_OK
        token2 = response.json()["access_token"]

        assert token1 != token2

        payload1 = decode_token_payload(token1)
        payload2 = decode_token_payload(token2)

        assert payload1["sub"] == payload2["sub"]
        assert payload1["exp"] != payload2["exp"]

    def test_login_success_with_protected_endpoint(self, controller, auth_user):
        """Test that a valid token can access protected endpoints"""
        me_response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.ME.switcher, headers=auth_user["headers"]
        )
        assert me_response.status_code == status.HTTP_200_OK

    def test_login_empty_username(self, controller, valid_headers):
        """Test that login fails with empty username"""
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            request_body={
                "username": "",
                "password": "anypassword",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Field 'username' cannot be empty"

    def test_login_empty_password(self, controller, valid_headers, registered_user):
        """Test that login fails with empty password"""
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            request_body={
                "username": registered_user["username"],
                "password": "",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Field 'password' cannot be empty"

    def test_login_invalid_username(self, controller, valid_headers):
        """Test that login fails with non-existent username"""
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            request_body={
                "username": TestData.NONEXISTENT_USER.value,
                "password": TestData.VALID_PASSWORD.value,
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == ErrorDetail.INVALID_CREDENTIALS.value

    def test_login_empty_fields(self, controller, valid_headers):
        """Test login with empty fields."""
        test_cases = [
            (
                {
                    "username": TestData.EMPTY_STRING.value,
                    "password": TestData.VALID_PASSWORD.value,
                },
                f"Field '{TestData.FIELD_USERNAME.value}' cannot be empty",
            ),
            (
                {
                    "username": TestData.TEST_USERNAME_ALT.value,
                    "password": TestData.EMPTY_STRING.value,
                },
                f"Field '{TestData.FIELD_PASSWORD.value}' cannot be empty",
            ),
            (
                {
                    "username": TestData.WHITESPACE_STRING.value,
                    "password": TestData.VALID_PASSWORD.value,
                },
                f"Field '{TestData.FIELD_USERNAME.value}' cannot be empty",
            ),
            (
                {
                    "username": TestData.TEST_USERNAME_ALT.value,
                    "password": TestData.WHITESPACE_STRING.value,
                },
                f"Field '{TestData.FIELD_PASSWORD.value}' cannot be empty",
            ),
            (
                {},
                ErrorDetail.FIELD_REQUIRED.value.format(TestData.FIELD_USERNAME.value),
            ),
            (
                {"password": TestData.VALID_PASSWORD.value},
                ErrorDetail.FIELD_REQUIRED.value.format(TestData.FIELD_USERNAME.value),
            ),
            (
                {"username": TestData.TEST_USERNAME_ALT.value},
                ErrorDetail.FIELD_REQUIRED.value.format(TestData.FIELD_PASSWORD.value),
            ),
        ]

        for request_body, expected_error in test_cases:
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.LOGIN.switcher,
                headers=valid_headers,
                request_body=request_body,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["detail"] == expected_error

    def test_login_with_spaces(self, controller, valid_headers, generate_unique_user):
        """Test login with spaces in credentials."""
        user_data = generate_unique_user()

        register_response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data,
        )
        assert register_response.status_code == status.HTTP_204_NO_CONTENT

        space_cases = [
            {
                "username": f" {user_data['username']}",
                "password": user_data["password"],
            },  # Leading space
            {
                "username": f"{user_data['username']} ",
                "password": user_data["password"],
            },  # Trailing space
            {
                "username": user_data["username"],
                "password": f" {user_data['password']}",
            },  # Leading space in password
            {
                "username": user_data["username"],
                "password": f"{user_data['password']} ",
            },  # Trailing space in password
        ]

        for case in space_cases:
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.LOGIN.switcher,
                headers=valid_headers,
                request_body=case,
            )

            assert (
                response.status_code == status.HTTP_401_UNAUTHORIZED
            ), f"Failed with case: {case}"

    def test_login_case_sensitivity(
        self, controller, valid_headers, generate_unique_user
    ):
        """Test username case sensitivity during login."""
        user_data = generate_unique_user()
        username = TestData.USERNAME_LOWERCASE.value.format(generate_random_string(4))
        user_data["username"] = username

        register_response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data,
        )
        assert register_response.status_code == status.HTTP_204_NO_CONTENT

        # Try to login with uppercase username
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            request_body={
                "username": username.upper(),
                "password": TestData.VALID_PASSWORD.value,
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == ErrorDetail.INVALID_CREDENTIALS.value

    def test_login_with_nonexistent_user(self, controller, valid_headers):
        """Test login with a username that doesn't exist."""
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            request_body={
                "username": TestData.NONEXISTENT_USER.value,
                "password": TestData.VALID_PASSWORD.value,
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == ErrorDetail.INVALID_CREDENTIALS.value

    def test_login_missing_fields(self, controller, valid_headers):
        """Test login with missing fields"""
        test_cases = [
            (
                {},
                ErrorDetail.FIELD_REQUIRED.value.format(TestData.FIELD_USERNAME.value),
            ),  # All fields missing
            (
                {"password": TestData.VALID_PASSWORD.value},
                ErrorDetail.FIELD_REQUIRED.value.format(TestData.FIELD_USERNAME.value),
            ),
            (
                {"username": TestData.TEST_USERNAME.value},
                ErrorDetail.FIELD_REQUIRED.value.format(TestData.FIELD_PASSWORD.value),
            ),
        ]

        for request_body, expected_error in test_cases:
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.LOGIN.switcher,
                headers=valid_headers,
                request_body=request_body,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["detail"] == expected_error


class TestDeleteEndpoint:
    def test_delete_user_success(self, controller, valid_headers, auth_user):
        """Test successful user deletion with valid token and password."""
        delete_data = {"password": auth_user["user"]["password"]}

        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.DELETE.switcher,
            headers=auth_user["headers"],
            request_body=delete_data,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not response.content

    def test_delete_already_deleted_user(self, controller, valid_headers, auth_user):
        """Test attempting to delete an already deleted user."""
        # First deletion
        delete_data = {"password": auth_user["user"]["password"]}

        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.DELETE.switcher,
            headers=auth_user["headers"],
            request_body=delete_data,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Try to delete again with same token
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.DELETE.switcher,
            headers=auth_user["headers"],
            request_body=delete_data,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == ErrorDetail.USER_NOT_FOUND.value

    def test_delete_user_wrong_password(self, controller, valid_headers, auth_user):
        """Test user deletion fails with wrong password."""
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.DELETE.switcher,
            headers=auth_user["headers"],
            request_body={"password": TestData.WRONG_PASSWORD.value},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == ErrorDetail.INVALID_PASSWORD.value

        # Test with empty password strings
        empty_passwords = [
            {"password": TestData.EMPTY_STRING.value},
            {"password": TestData.WHITESPACE_STRING.value},
        ]

        for request_body in empty_passwords:
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.DELETE.switcher,
                headers=auth_user["headers"],
                request_body=request_body,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["detail"] == ErrorDetail.PASSWORD_EMPTY.value

    def test_delete_missing_fields(self, controller, valid_headers, auth_user):
        """Test delete with missing fields"""
        test_cases = [
            (
                {},
                ErrorDetail.FIELD_REQUIRED.value.format(TestData.FIELD_PASSWORD.value),
            ),  # Password missing
            (
                {"wrong_field": "value"},
                ErrorDetail.FIELD_REQUIRED.value.format(TestData.FIELD_PASSWORD.value),
            ),  # Wrong field
        ]

        for request_body, expected_error in test_cases:
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.DELETE.switcher,
                headers=auth_user["headers"],
                request_body=request_body,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["detail"] == expected_error

    def test_delete_with_extra_fields(self, controller, valid_headers, auth_user):
        """Test delete with extra fields (should ignore them)"""
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.DELETE.switcher,
            headers=auth_user["headers"],
            request_body={
                "password": TestData.VALID_PASSWORD.value,
                "extra_field": "value",
            },
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_with_wrong_password(self, controller, valid_headers, auth_user):
        """Test delete with wrong password"""
        wrong_passwords = [
            TestData.WRONG_PASSWORD.value,
            TestData.WRONG_PASSWORD_VARIANT.value,
        ]

        for wrong_password in wrong_passwords:
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.DELETE.switcher,
                headers=auth_user["headers"],
                request_body={"password": wrong_password},
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["detail"] == ErrorDetail.INVALID_PASSWORD.value


class TestRegistrationBoundaries:
    def test_registration_with_long_inputs(self, controller, valid_headers):
        """Test that registration fails with overly long input values"""
        random_suffix1 = generate_random_string(100)
        test_data = {
            "username": random_suffix1,
            "email": f"test_{generate_random_string(10)}@example.com",
            "password": TestData.VALID_PASSWORD.value,
        }

        print(f"\nTesting long username:")
        print(f"Username length: {len(test_data['username'])} characters")
        print(f"Username: {test_data['username'][:50]}...{test_data['username'][-50:]}")

        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=test_data,
        )

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == ErrorDetail.USERNAME_TOO_LONG.value

        random_suffix2 = generate_random_string(10)
        local_part = generate_random_string(100)
        domain = generate_random_string(100)
        test_data = {
            "username": f"test_{random_suffix2}",
            "email": f"{local_part}@{domain}.com",
            "password": TestData.VALID_PASSWORD.value,
        }

        print(f"\nTesting long email:")
        print(f"Username: {test_data['username']}")
        print(f"Email length: {len(test_data['email'])} characters")
        print(f"Local part length: {len(local_part)} characters")
        print(f"Domain length: {len(domain)} characters")
        print(f"Email: {test_data['email'][:50]}...{test_data['email'][-50:]}")

        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=test_data,
        )

        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        error_msg = (
            f"Email with local part of {len(local_part)} chars and domain of {len(domain)} chars "
            f"should be invalid. Status: {response.status_code}, Response: {response.text}"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.json()["detail"] == ErrorDetail.EMAIL_LOCAL_PART_TOO_LONG.value
        ), error_msg

    def test_registration_with_special_characters(self, controller, valid_headers):
        """Test that registration fails with special characters in username"""
        for char in SPECIAL_CHARACTERS:
            random_suffix = generate_random_string(10)
            test_data = {
                "username": f"test{char}user{random_suffix}",
                "email": f"test_{random_suffix}@example.com",
                "password": f"ValidP@ss{random_suffix}1",
            }

            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body=test_data,
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert (
                response.json()["detail"]
                == ErrorDetail.USERNAME_INVALID_CHARACTERS.value
            )

    def test_registration_with_unicode_characters(self, controller, valid_headers):
        """Test that registration succeeds with non-ASCII unicode characters in username"""
        test_cases = [
            {"language": "chinese", "username": TestData.CHINESE_USERNAME.value},
            {"language": "bulgarian", "username": TestData.BULGARIAN_USERNAME.value},
            {"language": "arabic", "username": TestData.ARABIC_USERNAME.value},
            {"language": "korean", "username": TestData.KOREAN_USERNAME.value},
        ]

        for test_case in test_cases:
            random_suffix = generate_random_string(6)
            test_data = {
                "username": f"{test_case['username']}{random_suffix}",
                "email": f"test_{random_suffix}@example.com",
                "password": f"ValidP@ss{random_suffix}1",
            }

            print(
                f"\nTesting {test_case['language']} username: {test_data['username']}"
            )

            register_response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body=test_data,
            )

            print(f"Register response status: {register_response.status_code}")
            print(f"Register response body: {register_response.text}")

            assert (
                register_response.status_code == status.HTTP_204_NO_CONTENT
            ), f"Registration failed for {test_case['language']} username: {test_data['username']}"

            login_response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.LOGIN.switcher,
                headers=valid_headers,
                request_body={
                    "username": test_data["username"],
                    "password": test_data["password"],
                },
            )

            print(f"Login response status: {login_response.status_code}")
            print(f"Login response body: {login_response.text}")

            assert (
                login_response.status_code == status.HTTP_200_OK
            ), f"Login failed for {test_case['language']} username: {test_data['username']}"

            me_response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.ME.switcher,
                headers={
                    "Authorization": f"Bearer {login_response.json()['access_token']}",
                    **valid_headers,
                },
            )

            print(f"ME response status: {me_response.status_code}")
            print(f"ME response body: {me_response.text}")

            assert me_response.status_code == status.HTTP_200_OK
            assert me_response.json()["username"] == test_data["username"]


class TestRoleEndpoints:
    """Test cases for role-based functionality."""

    def test_register_with_valid_roles(
        self, controller, valid_headers, generate_unique_user
    ):
        """Test registration and login with valid role types (buyer and seller)."""
        valid_roles = ["buyer", "seller"]

        for role in valid_roles:
            user_data = generate_unique_user()
            user_data["role"] = role

            # Test registration
            register_response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body=user_data,
            )

            assert (
                register_response.status_code == status.HTTP_204_NO_CONTENT
            ), f"Failed to register user with role: {role}"

            # Test login
            login_response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.LOGIN.switcher,
                headers=valid_headers,
                request_body={
                    "username": user_data["username"],
                    "password": user_data["password"],
                },
            )

            assert (
                login_response.status_code == status.HTTP_200_OK
            ), f"Failed to login user with role: {role}"
            assert "access_token" in login_response.json()

            # Test /me endpoint to verify role
            token = login_response.json()["access_token"]
            me_headers = {**valid_headers, "Authorization": f"Bearer {token}"}
            me_response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.ME.switcher,
                headers=me_headers,
            )

            assert me_response.status_code == status.HTTP_200_OK
            assert me_response.json()["role"] == role

    def test_register_with_admin_role_fails(
        self, controller, valid_headers, generate_unique_user
    ):
        """Test registration and login fails when trying to create an admin account."""
        user_data = generate_unique_user()
        user_data["role"] = "admin"

        # Test registration fails
        register_response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data,
        )

        assert register_response.status_code == status.HTTP_403_FORBIDDEN
        assert (
            register_response.json()["detail"]
            == ErrorDetail.ADMIN_REGISTRATION_FORBIDDEN.value
        )

        # Try to login (should fail as registration failed)
        login_response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            request_body={
                "username": user_data["username"],
                "password": user_data["password"],
            },
        )

        assert login_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert login_response.json()["detail"] == ErrorDetail.INVALID_CREDENTIALS.value

    def test_register_with_invalid_role(
        self, controller, valid_headers, generate_unique_user
    ):
        """Test registration fails with invalid role."""
        user_data = generate_unique_user()
        user_data["role"] = "invalid_role"

        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == ErrorDetail.INVALID_ROLE.value


class TestTokenValidation:
    def test_invalid_token_format(self, controller, valid_headers):
        """Test various invalid token formats."""
        test_cases = [
            (
                TestData.INVALID_TOKEN.value,
                ErrorDetail.NOT_AUTHENTICATED.value,
            ),  # No Bearer prefix
            (
                TestData.BEARER_NO_TOKEN.value,
                ErrorDetail.TOKEN_INVALID.value,
            ),  # Has Bearer but no token
            (
                TestData.BEARER_EMPTY_TOKEN.value,
                ErrorDetail.TOKEN_INVALID.value,
            ),  # Has Bearer but empty token
            (
                TestData.INVALID_JWT.value,
                ErrorDetail.TOKEN_INVALID.value,
            ),  # Invalid JWT
            (
                TestData.WRONG_PREFIX_TOKEN.value,
                ErrorDetail.NOT_AUTHENTICATED.value,
            ),  # Wrong prefix
            (
                TestData.EMPTY_TOKEN.value,
                ErrorDetail.NOT_AUTHENTICATED.value,
            ),  # Empty string
            (None, ErrorDetail.NOT_AUTHENTICATED.value),  # Missing header
        ]

        for token, expected_error in test_cases:
            headers = valid_headers.copy()
            if token is not None:
                headers["Authorization"] = token
            else:
                headers.pop("Authorization", None)

            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.DELETE.switcher,
                headers=headers,
                request_body={"password": TestData.VALID_PASSWORD.value},
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["detail"] == expected_error

    def test_expired_token(self, controller, valid_headers, generate_unique_user):
        """Test using an expired token."""

        user_data = generate_unique_user()
        register_response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.REGISTER.switcher,
            headers=valid_headers,
            request_body=user_data,
        )
        assert register_response.status_code == status.HTTP_204_NO_CONTENT

        expired_time = datetime.utcnow() - timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES + 1
        )
        expired_token = jwt.encode(
            {"sub": user_data["username"], "exp": expired_time},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        headers = {**valid_headers, "Authorization": f"Bearer {expired_token}"}
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.ME.switcher,
            headers=headers,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == ErrorDetail.TOKEN_EXPIRED.value

    def test_protected_endpoint_without_token(self, controller, valid_headers):
        """Test that protected endpoint fails without token"""
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.ME.switcher, headers=valid_headers
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == ErrorDetail.NOT_AUTHENTICATED.value

    def test_protected_endpoint_with_malformed_token(self, controller, valid_headers):
        """Test that protected endpoint fails with malformed token"""
        malformed_tokens = [
            (
                TestData.INVALID_TOKEN.value,
                status.HTTP_401_UNAUTHORIZED,
                ErrorDetail.NOT_AUTHENTICATED.value,
            ),
            (
                TestData.MALFORMED_JWT.value,
                status.HTTP_401_UNAUTHORIZED,
                ErrorDetail.TOKEN_INVALID.value,
            ),
            (
                TestData.LONG_TOKEN.value,
                status.HTTP_401_UNAUTHORIZED,
                ErrorDetail.TOKEN_INVALID.value,
            ),
            (
                TestData.EXTRA_DOTS_TOKEN.value,
                status.HTTP_401_UNAUTHORIZED,
                ErrorDetail.TOKEN_INVALID.value,
            ),
            (
                TestData.BEARER_EMPTY_TOKEN.value,
                status.HTTP_401_UNAUTHORIZED,
                ErrorDetail.TOKEN_INVALID.value,
            ),
            (
                TestData.SINGLE_PART_TOKEN.value,
                status.HTTP_401_UNAUTHORIZED,
                ErrorDetail.TOKEN_INVALID.value,
            ),
        ]

        for token, expected_status, expected_error in malformed_tokens:
            headers = valid_headers.copy()
            headers["Authorization"] = token

            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.DELETE.switcher,
                headers=headers,
                request_body={"password": TestData.VALID_PASSWORD.value},
            )

            assert response.status_code == expected_status
            assert response.json()["detail"] == expected_error


class TestRegistrationValidation:
    def test_invalid_password_patterns(self, controller, valid_headers):
        """Test registration with invalid password patterns"""
        test_cases = [
            (
                TestData.INVALID_PASSWORD_NO_UPPER.value,
                ErrorDetail.PASSWORD_MISSING_UPPERCASE.value,
            ),
            (
                TestData.INVALID_PASSWORD_NO_LOWER.value,
                ErrorDetail.PASSWORD_MISSING_LOWERCASE.value,
            ),
            (
                TestData.INVALID_PASSWORD_NO_NUMBERS.value,
                ErrorDetail.PASSWORD_MISSING_DIGIT.value,
            ),
            (
                TestData.INVALID_PASSWORD_NO_SPECIAL.value,
                ErrorDetail.PASSWORD_MISSING_SPECIAL.value,
            ),
            (
                TestData.INVALID_PASSWORD_SHORT.value,
                ErrorDetail.PASSWORD_TOO_SHORT.value,
            ),
        ]

        for password, expected_error in test_cases:
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body={
                    "username": TestData.USERNAME_PATTERN.value.format(
                        generate_random_string(8)
                    ),
                    "email": TestData.EMAIL_PATTERN.value.format(
                        generate_random_string(8)
                    ),
                    "password": password,
                },
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["detail"] == expected_error

    def test_invalid_username_patterns(self, controller, valid_headers):
        """Test registration with invalid username patterns"""
        test_cases = [
            (
                TestData.INVALID_USERNAME_TOO_SHORT.value,
                ErrorDetail.USERNAME_TOO_SHORT.value,
            ),
            (
                TestData.INVALID_USERNAME_TOO_LONG.value,
                ErrorDetail.USERNAME_TOO_LONG.value,
            ),
            (
                TestData.INVALID_USERNAME_SPECIAL_CHARS.value,
                ErrorDetail.USERNAME_INVALID_CHARACTERS.value,
            ),
            (
                TestData.INVALID_USERNAME_SPACES.value,
                ErrorDetail.USERNAME_INVALID_CHARACTERS.value,
            ),
        ]

        for username, expected_error in test_cases:
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body={
                    "username": username,
                    "email": TestData.VALID_EMAIL_PATTERN.value.format(
                        generate_random_string(8)
                    ),
                    "password": TestData.VALID_PASSWORD.value,
                },
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["detail"] == expected_error

    def test_password_requirements(self, controller, valid_headers):
        """Test that password requirements are enforced"""
        invalid_passwords = [
            (
                TestData.INVALID_PASSWORD_SHORT.value,
                ErrorDetail.PASSWORD_TOO_SHORT.value,
            ),
            (
                TestData.INVALID_PASSWORD_NO_UPPER.value,
                ErrorDetail.PASSWORD_MISSING_UPPERCASE.value,
            ),
            (
                TestData.INVALID_PASSWORD_NO_LOWER.value,
                ErrorDetail.PASSWORD_MISSING_LOWERCASE.value,
            ),
            (
                TestData.INVALID_PASSWORD_NO_SPECIAL.value,
                ErrorDetail.PASSWORD_MISSING_SPECIAL.value,
            ),
            (
                TestData.INVALID_PASSWORD_NO_NUMBERS.value,
                ErrorDetail.PASSWORD_MISSING_DIGIT.value,
            ),
            (
                TestData.INVALID_PASSWORD_SHORT_WITH_REQS.value,
                ErrorDetail.PASSWORD_TOO_SHORT.value,
            ),
        ]

        for password, expected_error in invalid_passwords:
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body={
                    "username": TestData.USERNAME_PATTERN.value.format(
                        generate_random_string(8)
                    ),
                    "email": TestData.EMAIL_PATTERN.value.format(
                        generate_random_string(8)
                    ),
                    "password": password,
                },
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["detail"] == expected_error


class TestAuthenticationMiddleware:
    def test_invalid_token_format(self, controller, valid_headers):
        """Test various invalid token formats."""
        test_cases = [
            (
                TestData.INVALID_TOKEN.value,
                ErrorDetail.NOT_AUTHENTICATED.value,
            ),  # No Bearer prefix
            (
                TestData.BEARER_NO_TOKEN.value,
                ErrorDetail.TOKEN_INVALID.value,
            ),  # Has Bearer but no token
            (
                TestData.BEARER_EMPTY_TOKEN.value,
                ErrorDetail.TOKEN_INVALID.value,
            ),  # Has Bearer but empty token
            (
                TestData.INVALID_JWT.value,
                ErrorDetail.TOKEN_INVALID.value,
            ),  # Invalid JWT
            (
                TestData.WRONG_PREFIX_TOKEN.value,
                ErrorDetail.NOT_AUTHENTICATED.value,
            ),  # Wrong prefix
            (
                TestData.EMPTY_TOKEN.value,
                ErrorDetail.NOT_AUTHENTICATED.value,
            ),  # Empty string
            (None, ErrorDetail.NOT_AUTHENTICATED.value),  # Missing header
        ]

        for token, expected_error in test_cases:
            headers = valid_headers.copy()
            if token is not None:
                headers["Authorization"] = token
            else:
                headers.pop("Authorization", None)

            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.DELETE.switcher,
                headers=headers,
                request_body={"password": TestData.VALID_PASSWORD.value},
            )

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert response.json()["detail"] == expected_error
