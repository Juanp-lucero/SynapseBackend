from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.user import UserLogin, Token
from app.core.security import (
    verify_password,
    create_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=Token)
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

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }