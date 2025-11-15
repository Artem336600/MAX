"""
API для авторизации через MAKS credentials
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import hashlib

from core.database import get_db
from models.user import User
from core.security import create_access_token

router = APIRouter(prefix="/api/v1/maks-auth", tags=["MAKS Auth"])


class MAKSLoginRequest(BaseModel):
    """Запрос на вход через MAKS"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Ответ при успешном входе"""
    access_token: str
    token_type: str = "bearer"
    user: dict


def hash_password(password: str) -> str:
    """Хеширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()


@router.post("/login", response_model=LoginResponse)
async def maks_login(
    request: MAKSLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Вход через MAKS credentials
    
    Логин и пароль выдаются ботом при команде /start
    """
    # Найти пользователя по maks_username
    result = await db.execute(
        select(User).where(User.maks_username == request.username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль"
        )
    
    # Проверить пароль
    password_hash = hash_password(request.password)
    if user.password_hash != password_hash:
        raise HTTPException(
            status_code=401,
            detail="Неверный логин или пароль"
        )
    
    # Создать токен
    access_token = create_access_token({"sub": user.id})
    
    return LoginResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "maks_username": user.maks_username
        }
    )


@router.get("/check-username/{username}")
async def check_username(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    """Проверить существует ли логин"""
    result = await db.execute(
        select(User).where(User.maks_username == username)
    )
    user = result.scalar_one_or_none()
    
    return {
        "exists": user is not None,
        "username": username
    }
