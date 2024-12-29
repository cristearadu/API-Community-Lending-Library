import base64
import json
import random
import string


def decode_token_payload(token):
    """Decode JWT token payload."""
    payload = token.split(".")[1]
    payload += "=" * (4 - len(payload) % 4)
    return json.loads(base64.b64decode(payload))


def generate_random_string(length):
    """Generate a random string of specified length."""
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))
