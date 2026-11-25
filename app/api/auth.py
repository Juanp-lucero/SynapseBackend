from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import UserLogin, Token
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    validate_refresh_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    response_model=Token
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    if not verify_password(
        user_data.password,
        user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    access_token = create_access_token({
        "sub": str(user.id),
        "email": user.email
    })

    refresh_token = create_refresh_token(
        db,
        user.id
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post(
    "/refresh",
    response_model=Token
)
def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):

    stored_token = validate_refresh_token(
        db,
        refresh_token
    )

    if stored_token is None:

        raise HTTPException(
            status_code=401,
            detail="Refresh token inválido o expirado"
        )

    user = db.query(User).filter(
        User.id == stored_token.user_id
    ).first()

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado"
        )

    access_token = create_access_token({
        "sub": str(user.id),
        "email": user.email
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(
    refresh_token: str,
    db: Session = Depends(get_db)
):

    stored_token = db.query(
        RefreshToken
    ).filter(
        RefreshToken.token == refresh_token
    ).first()

    if stored_token is None:

        raise HTTPException(
            status_code=401,
            detail="Refresh token inválido"
        )

    db.delete(stored_token)

    db.commit()

    return {
        "message": "Sesión cerrada correctamente"
    }