from http import HTTPStatus
import secrets

from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials


def basic_auth(credentials: HTTPBasicCredentials, username: str, password: str) -> str:
    is_correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"),
        username,
    )
    is_correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"),
        password,
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return credentials.username
