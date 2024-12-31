from enum import Enum, auto
from functools import partial
import requests
from typing import Optional, Dict, Any


class AuthenticationEndpoints(Enum):
    """Enum for authentication endpoints."""

    REGISTER = ("POST", "http://127.0.0.1:8000/register", "REGISTER USER")
    LOGIN = ("POST", "http://127.0.0.1:8000/login", "LOGIN USER")
    ME = ("GET", "http://127.0.0.1:8000/users/me", "GET CURRENT USER")
    DELETE = ("DELETE", "http://127.0.0.1:8000/users/me", "DELETE CURRENT USER")

    def __init__(self, request_type: str, path: str, switcher: str):
        self.request_type = request_type
        self.path = path
        self.switcher = switcher


def http_request(
    request_type: str,
    url: str,
    headers: Dict[str, str],
    request_body: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    **kwargs
) -> requests.Response:
    """
    Generic HTTP request function.

    Args:
        request_type: HTTP method (GET, POST, etc.)
        url: The endpoint URL
        headers: Request headers
        request_body: Request body for POST/PUT requests
        params: URL parameters
        **kwargs: Additional arguments for the request

    Returns:
        Response object from the request
    """
    request_method = getattr(requests, request_type.lower())

    if request_body is not None:
        response = request_method(url, headers=headers, json=request_body, **kwargs)
    else:
        response = request_method(url, headers=headers, params=params, **kwargs)

    return response


class AuthenticationController:
    """Controller for authentication-related API requests."""

    def authentication_request_controller(
        self,
        key: str,
        headers: Dict[str, str],
        request_body: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """Handle authentication requests based on the endpoint key."""

        # Handle request body for registration
        if key == AuthenticationEndpoints.REGISTER.switcher and request_body:
            if "role" not in request_body:
                request_body["role"] = "buyer"  # lowercase role

        switcher = {
            AuthenticationEndpoints.REGISTER.switcher: partial(
                http_request,
                AuthenticationEndpoints.REGISTER.request_type,
                AuthenticationEndpoints.REGISTER.path,
                headers,
                request_body,
                None,
            ),
            AuthenticationEndpoints.LOGIN.switcher: partial(
                http_request,
                AuthenticationEndpoints.LOGIN.request_type,
                AuthenticationEndpoints.LOGIN.path,
                headers,
                request_body,
                None,
            ),
            AuthenticationEndpoints.ME.switcher: partial(
                http_request,
                AuthenticationEndpoints.ME.request_type,
                AuthenticationEndpoints.ME.path,
                headers,
                None,
                None,
            ),
            AuthenticationEndpoints.DELETE.switcher: partial(
                http_request,
                AuthenticationEndpoints.DELETE.request_type,
                AuthenticationEndpoints.DELETE.path,
                headers,
                request_body,
                None,
            ),
        }
        return switcher.get(key)()
