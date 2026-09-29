import os
import secrets

from datetime import datetime, timedelta, timezone

import jwt

from pwdlib import PasswordHash
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken


load_dotenv()


password_hash = PasswordHash.recommended()


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "synapse-clave-secreta-desarrollo"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

REFRESH_TOKEN_EXPIRE_DAYS = 30


security = HTTPBearer()


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return password_hash.verify(
        plain_password,
        hashed_password
    )


def get_password_hash(
    password: str
) -> str:

    return password_hash.hash(
        password
    )


def create_access_token(
    data: dict
) -> str:

    to_encode = data.copy()

    expire = datetime.now(
        timezone.utc
    ) + timedelta(
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


def create_refresh_token(
    db: Session,
    user_id: int
) -> str:

    token = secrets.token_urlsafe(64)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    refresh_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )

    db.add(refresh_token)

    db.commit()

    db.refresh(refresh_token)

    return token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el usuario",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (
        jwt.PyJWTError,
        ValueError
    ):

        raise credentials_exception

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise credentials_exception

    return user


def validate_refresh_token(
    db: Session,
    token: str
):

    refresh_token = db.query(
        RefreshToken
    ).filter(
        RefreshToken.token == token
    ).first()

    if refresh_token is None:
        return None

    now = datetime.now(timezone.utc)

    expires_at = refresh_token.expires_at

    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if expires_at <= now:

        db.delete(refresh_token)
        db.commit()

        return None

    return refresh_token