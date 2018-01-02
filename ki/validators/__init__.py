import socket
import uuid
from urllib.parse import urlparse

from ki.errors import ValidationError


def validate_url(url, **kwargs):
    if not url and kwargs.get("allow_empty", False):
        return True
    if not url:
        raise ValidationError(
            "Invalid URL"
        )
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    validate_domain(host)
    return True


def validate_domain(domain):
    try:
        socket.gethostbyname(domain)
    except Exception:
        raise ValidationError(
            "Invalid domain"
        )
    return True


def validate_email(email):
    """Doesn't even attempt to validate the
    username part (just if not empty)"""
    email = str(email or "")
    ok = False

    email = (email.strip() or "")
    parts = email.split("@")
    ok = (len(parts) == 2)

    if ok and not (parts[0] and parts[1]):
        ok = False
    elif len(parts) > 1:
        validate_domain(parts[1])

    if not ok:
        raise ValidationError("Invalid email")

    return ok


def validate_password(password):
    if not password:
        raise ValidationError(
            "Password is empty"
        )

    password = str(password)

    if len(password) < 6:
        raise ValidationError(
            "Password too short (min: 6, max: 256)"
        )
    elif len(password) > 256:
        raise ValidationError(
            "Password too long (max: 256)"
        )

    return True


def validate_username(name):
    if not name:
        raise ValidationError(
            "Username empty"
        )

    if name[0].isspace() or name[-1].isspace():
        raise ValidationError(
            "Username must not start or end with whitespace"
        )

    name = name.strip()
    if len(name) < 3:
        raise ValidationError(
            "Username too short (min: 3, max: 32)"
        )
    elif len(name) > 32:
        raise ValidationError(
            "Username too long (max: 32)"
        )

    return True


def validate_user_id(id):
    try:
        uuid.UUID(str(id))
    except ValueError as e:
        raise ValidationError("Invalid user id")

    return True
