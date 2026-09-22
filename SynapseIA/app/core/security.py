import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from dotenv import load_dotenv


load_dotenv()

password_hash = PasswordHash.recommended()

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "synapse-clave-secreta-desarrollo"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password
    )


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt