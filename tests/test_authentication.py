import pytest
import time
from tests.constants import (
    ErrorDetail,
    SPECIAL_CHARACTERS,
    INVALID_EMAIL_FORMATS,
    UserRole
)
from tests.controllers import AuthenticationEndpoints
from tests.utils.string_generators import (
    generate_unicode_test_cases,
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
            "password": "ValidP@ss1",
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
        user_data["username"] = "ab"  # 2 characters
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

    def test_register_invalid_password(
        self, controller, valid_headers, generate_unique_user
    ):
        """Test registration fails with invalid password format."""
        invalid_passwords = [
            ("short", ErrorDetail.PASSWORD_TOO_SHORT),
            ("nouppercase1!", ErrorDetail.PASSWORD_MISSING_UPPERCASE),
            ("NOLOWERCASE1!", ErrorDetail.PASSWORD_MISSING_LOWERCASE),
            ("NoDigits!", ErrorDetail.PASSWORD_MISSING_DIGIT),
            ("NoSpecial1", ErrorDetail.PASSWORD_MISSING_SPECIAL),
        ]

        for password, expected_error in invalid_passwords:
            user_data = generate_unique_user()
            user_data["password"] = password
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body=user_data,
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert (
                response.json()["detail"] == expected_error.value
            ), f"Failed for {password}"

    def test_password_complexity(self, controller, valid_headers, generate_unique_user):
        """Test password complexity requirements."""
        user_data = generate_unique_user()
        invalid_passwords = [
            "short",           # Too short
            "nouppercase123",  # No uppercase
            "NOLOWERCASE123",  # No lowercase
            "NoSpecial123",    # No special characters
            "No@Numbers",      # No numbers
            "Ab@1",           # Too short but with all requirements
        ]
        
        for invalid_pass in invalid_passwords:
            user_data["password"] = invalid_pass
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body=user_data,
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Password must" in response.text  # Generic check for password requirements message

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

    def test_username_special_cases(self, controller, valid_headers, generate_unique_user):
        """Test special username cases."""
        invalid_usernames = [
            " " * 10,                  # Only spaces
            " leading_space",          # Leading space
            "trailing_space ",         # Trailing space
            "space in middle",         # Space in middle
            "special@character",       # Special characters
            "hyphen-name",             # Hyphens
            "dot.name",                # Dots
        ]
        
        for invalid_username in invalid_usernames:
            user_data = generate_unique_user()
            user_data["username"] = invalid_username
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body=user_data,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST, \
                f"Failed with {response.status_code} for username: '{invalid_username}'"
            
            error_detail = response.json()["detail"]
            assert error_detail == ErrorDetail.USERNAME_CAN_ONLY_CONTAIN.value, \
                (f"Expected '{ErrorDetail.USERNAME_CAN_ONLY_CONTAIN.value}' but got '{error_detail}' "
                 f"for username: '{invalid_username}'")

    def test_valid_username_formats(self, controller, valid_headers, generate_unique_user):
        """Test valid username formats."""
        unique_suffix = generate_random_string(4)
        
        valid_username_patterns = [
            f"usr{unique_suffix}",        # Letters and numbers
            f"123{unique_suffix}",        # Numbers at start
            f"usr_{unique_suffix}",       # With underscore
            f"ABC{unique_suffix}",        # Uppercase
            f"low{unique_suffix}",        # Lowercase
        ]
        
        for valid_username in valid_username_patterns:
            user_data = generate_unique_user()
            user_data["username"] = valid_username
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body=user_data,
            )

            assert response.status_code == status.HTTP_204_NO_CONTENT, \
                f"Failed to register with valid username: '{valid_username}'. Error: {response.text}"
            
            # Verify the length is within bounds
            assert 3 <= len(valid_username) <= 30, \
                f"Username '{valid_username}' length ({len(valid_username)}) is outside allowed range (3-30)"

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
            }
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

    def test_role_case_sensitivity(self, controller, valid_headers, generate_unique_user):
        """Test role case sensitivity."""
        role_variations = [
            "BUYER",
            "Buyer",
            "buyer",
            "SELLER",
            "Seller",
            "seller",
        ]
        
        for role in role_variations:
            user_data = generate_unique_user()
            user_data["role"] = role
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.REGISTER.switcher,
                headers=valid_headers,
                request_body=user_data,
            )
            assert response.status_code == status.HTTP_204_NO_CONTENT


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
        assert response.json()["detail"] == ErrorDetail.USERNAME_EMPTY.value

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
        assert response.json()["detail"] == ErrorDetail.PASSWORD_EMPTY.value

    def test_login_invalid_username(self, controller, valid_headers):
        """Test that login fails with non-existent username"""
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            request_body={
                "username": "nonexistent_user",
                "password": "ValidPassword1!",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == ErrorDetail.INVALID_CREDENTIALS.value

    def test_protected_endpoint_without_token(self, controller, valid_headers):
        """Test that protected endpoint fails without token (Forbidden)"""
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.ME.switcher, headers=valid_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_protected_endpoint_with_malformed_token(self, controller, valid_headers):
        """Test that protected endpoint fails with malformed token"""
        malformed_tokens = [
            ("not_a_token", status.HTTP_403_FORBIDDEN),
            ("Bearer not.a.token", status.HTTP_401_UNAUTHORIZED),
            ("Bearer " + "a" * 100, status.HTTP_401_UNAUTHORIZED),
            ("Bearer token.with.two.dots.only", status.HTTP_401_UNAUTHORIZED),
            ("Bearer ", status.HTTP_403_FORBIDDEN),
            ("Bearer token", status.HTTP_401_UNAUTHORIZED),
        ]

        for token, expected_status in malformed_tokens:
            print(f"Token and expected status: {token}, {expected_status}")
            invalid_auth_headers = {**valid_headers, "Authorization": token}
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.ME.switcher, headers=invalid_auth_headers
            )
            assert response.status_code == expected_status
            if expected_status == status.HTTP_401_UNAUTHORIZED:
                assert response.json()["detail"] == ErrorDetail.TOKEN_INVALID.value


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
        delete_data = {"password": "WrongPassword123!"}

        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.DELETE.switcher,
            headers=auth_user["headers"],
            request_body=delete_data,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == ErrorDetail.INVALID_PASSWORD.value

        # Test with empty password strings
        empty_passwords = [
            {"password": ""},
            {"password": "   "},
        ]

        for data in empty_passwords:
            response = controller.authentication_request_controller(
                key=AuthenticationEndpoints.DELETE.switcher,
                headers=auth_user["headers"],
                request_body=data,
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json()["detail"] == ErrorDetail.PASSWORD_EMPTY.value

        # Test with missing password field
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.DELETE.switcher,
            headers=auth_user["headers"],
            request_body={},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert ErrorDetail.FIELD_REQUIRED.value in response.text.lower()


class TestRegistrationBoundaries:
    def test_registration_with_long_inputs(self, controller, valid_headers):
        """Test that registration fails with overly long input values"""
        random_suffix1 = generate_random_string(100)
        test_data = {
            "username": random_suffix1,
            "email": f"test_{generate_random_string(10)}@example.com",
            "password": "ValidP@ss1",
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
            "password": "ValidP@ss1",
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
        test_cases = generate_unicode_test_cases()

        for test_case in test_cases:
            random_suffix = generate_random_string(10)
            test_data = {
                "username": test_case["username"],
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
        assert response.json()["detail"] == "Invalid role"
