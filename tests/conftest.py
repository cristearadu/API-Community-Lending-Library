import pytest
from tests.utils.string_generators import generate_random_string
from tests.constants import StatusCode
from tests.controllers import AuthenticationController, AuthenticationEndpoints


@pytest.fixture
def controller():
    """Fixture that provides an authentication controller instance."""
    return AuthenticationController()


@pytest.fixture
def valid_headers():
    """Fixture that provides valid headers for API requests."""
    return {
        "accept": "application/json",
        "Content-Type": "application/json",
    }


@pytest.fixture
def generate_unique_user():
    """Fixture to generate a unique user with random data."""

    def _generate(prefix="user"):
        unique_suffix = generate_random_string(8)
        return {
            "username": f"{prefix}_{unique_suffix}",
            "email": f"{prefix}_{unique_suffix}@example.com",
            "password": f"ValidP@ss{unique_suffix}1",
        }

    return _generate


@pytest.fixture
def registered_user(controller, valid_headers, generate_unique_user):
    """Fixture that creates and returns a registered user."""
    user_data = generate_unique_user()
    response = controller.authentication_request_controller(
        key=AuthenticationEndpoints.REGISTER.switcher,
        headers=valid_headers,
        request_body=user_data,
    )
    assert response.status_code == StatusCode.SUCCESS.value
    return user_data


@pytest.fixture
def auth_user(controller, valid_headers, generate_unique_user):
    """
    Fixture that registers a user, logs in, and returns auth token.
    In the future, will also handle cleanup.
    """
    user_data = generate_unique_user()
    register_response = controller.authentication_request_controller(
        key=AuthenticationEndpoints.REGISTER.switcher,
        headers=valid_headers,
        request_body=user_data,
    )
    assert register_response.status_code == StatusCode.SUCCESS.value

    login_response = controller.authentication_request_controller(
        key=AuthenticationEndpoints.LOGIN.switcher,
        headers=valid_headers,
        username=user_data["username"],
        password=user_data["password"],
    )
    assert login_response.status_code == StatusCode.SUCCESS.value
    token = login_response.json()["access_token"]

    auth_headers = {**valid_headers, "Authorization": f"Bearer {token}"}

    auth_data = {"user": user_data, "token": token, "headers": auth_headers}

    yield auth_data

    # Teardown (to be implemented)
    # TODO: Implement user deletion
    # try:
    #     delete_response = controller.authentication_request_controller(
    #         key=AuthenticationEndpoints.DELETE_USER.switcher,
    #         headers=auth_headers
    #     )
    #     assert delete_response.status_code == StatusCode.SUCCESS.value
    # except Exception as e:
    #     print(f"Error during user cleanup: {e}")
