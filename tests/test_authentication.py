import time
from tests.constants import (
    ErrorDetail,
    SPECIAL_CHARACTERS,
    INVALID_EMAIL_FORMATS,
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
        assert "Username already registered" in response.text

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
            assert response.json()["detail"] == expected_error.value, f"Failed for {password}"


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
            username=auth_user["user"]["username"],
            password=auth_user["user"]["password"],
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
            key=AuthenticationEndpoints.ME.switcher, 
            headers=auth_user["headers"]
        )
        assert me_response.status_code == status.HTTP_200_OK

    def test_login_empty_username(self, controller, valid_headers):
        """Test that login fails with empty username"""
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            username="",
            password="anypassword",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == ErrorDetail.USERNAME_EMPTY.value

    def test_login_empty_password(self, controller, valid_headers, registered_user):
        """Test that login fails with empty password"""
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            username=registered_user["username"],
            password="",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == ErrorDetail.PASSWORD_EMPTY.value

    def test_login_invalid_username(self, controller, valid_headers):
        """Test that login fails with non-existent username"""
        response = controller.authentication_request_controller(
            key=AuthenticationEndpoints.LOGIN.switcher,
            headers=valid_headers,
            username="nonexistent_user",
            password="ValidPassword1!",
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
                username=test_data["username"],
                password=test_data["password"],
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
