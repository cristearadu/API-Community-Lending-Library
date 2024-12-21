from enum import Enum
from functools import partial
from tests.requests_builder import http_request


class AuthenticationEndpoints(Enum):
    REGISTER = ("POST", "http://127.0.0.1:8000/register", "REGISTER USER")
    LOGIN = ("POST", "http://127.0.0.1:8000/login", "LOGIN USER")

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
                headers, None, None
            ),
            AuthenticationEndpoints.LOGIN.switcher: partial(
                http_request,
                AuthenticationEndpoints.LOGIN.request_type,
                AuthenticationEndpoints.LOGIN.path,
                headers, None, None
            )
        }
        if key in switcher:
            return switcher[key]()
        else:
            raise ValueError(f"Invalid key: {key}")


controller_cards = AuthenticationController()
x = controller_cards.authentication_request_controller(
    key=AuthenticationEndpoints.REGISTER.switcher,
    headers={"accept": "application/json",
             "content-type": "application/json"}
    # request_body={
    #     "username": "f1",
    #     "email": "f1@gmail.com",
    #     "password": "Passss1!"
    # }
)
print(x)
x = controller_cards.authentication_request_controller(
    key=AuthenticationEndpoints.LOGIN.switcher,
    headers={"accept": "application/json",
             "content-type": "application/json"}
    # request_body={
    #     "username": "f1",
    #     "email": "f1@gmail.com",
    #     "password": "Passss1!"
    # }
)
print(x)
