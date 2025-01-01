import logging
import sys
from datetime import datetime
import json
from fastapi import Request
import emoji
from starlette.responses import Response, JSONResponse
from typing import Union


class CustomFormatter(logging.Formatter):
    """Custom formatter with colors and emojis"""

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    reset = "\x1b[0m"
    green = "\x1b[32m"
    blue = "\x1b[34m"

    EMOJIS = {
        "success": emoji.emojize(":check_mark_button:"),
        "warning": emoji.emojize(":warning:"),
        "error": emoji.emojize(":cross_mark:"),
        "info": emoji.emojize(":information:"),
    }

    def format(self, record):
        if hasattr(record, "status_code"):
            if record.status_code < 300:
                color = self.green
                status_emoji = self.EMOJIS["success"]
            elif record.status_code < 400:
                color = self.blue
                status_emoji = self.EMOJIS["info"]
            elif record.status_code < 500:
                color = self.yellow
                status_emoji = self.EMOJIS["warning"]
            else:
                color = self.red
                status_emoji = self.EMOJIS["error"]
        else:
            color = self.grey
            status_emoji = self.EMOJIS["info"]

        log_message = (
            f"{status_emoji} {color}%(asctime)s - %(levelname)s - "
            f"%(method)s %(path)s - %(status_code)s{self.reset}"
        )

        if hasattr(record, "request_headers"):
            log_message += (
                f"\n{self.blue}Request Headers:{self.reset}\n%(request_headers)s"
            )
        if hasattr(record, "request_body"):
            log_message += f"\n{self.blue}Request Body:{self.reset}\n%(request_body)s"
        if hasattr(record, "response_headers"):
            log_message += (
                f"\n{self.green}Response Headers:{self.reset}\n%(response_headers)s"
            )
        if hasattr(record, "response_body"):
            log_message += (
                f"\n{self.green}Response Body:{self.reset}\n%(response_body)s"
            )

        formatter = logging.Formatter(log_message, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


# Initialize logger
logger = logging.getLogger("api")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(CustomFormatter())
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler("api.log")
file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(levelname)s - %(method)s %(path)s - %(status_code)s\n"
        "Request Headers: %(request_headers)s\n"
        "Request Body: %(request_body)s\n"
        "Response Headers: %(response_headers)s\n"
        "Response Body: %(response_body)s\n"
    )
)
logger.addHandler(file_handler)


async def log_request_middleware(request: Request, call_next):
    """Non-blocking logging middleware"""
    # Get request details
    request_body = None
    try:
        body = await request.body()
        if body:
            request_body = json.loads(body)

            # Reconstruct request body for downstream middleware
            async def receive():
                return {"type": "http.request", "body": body}

            request._receive = receive
    except:
        pass

    request_headers = dict(request.headers)

    # Clean up sensitive data
    if "authorization" in request_headers:
        request_headers["authorization"] = "***"
    if request_body and isinstance(request_body, dict):
        if "password" in request_body:
            request_body["password"] = "***"

    # Process request
    response = await call_next(request)

    # Get response details
    response_body = None
    try:
        if isinstance(response, JSONResponse):
            response_body = response.body.decode()
            try:
                response_body = json.loads(response_body)
            except:
                pass
    except:
        pass

    # Prepare extra fields for logger
    extra = {
        "path": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
        "request_headers": json.dumps(request_headers, indent=2),
        "request_body": json.dumps(request_body, indent=2) if request_body else None,
        "response_headers": json.dumps(dict(response.headers), indent=2),
        "response_body": json.dumps(response_body, indent=2) if response_body else None,
    }

    # Log with appropriate level based on status code
    if response.status_code < 400:
        logger.info("", extra=extra)
    elif response.status_code < 500:
        logger.warning("", extra=extra)
    else:
        logger.error("", extra=extra)

    return response
