from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional

from core.database import get_db
from core.security import hash_password, verify_password, create_access_token, decode_access_token
from models.user import User

router = APIRouter()
security = HTTPBearer()

# Pydantic schemas
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: str

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    token: str
    user: UserResponse

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password)
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create access token
    token = create_access_token(data={"sub": user.id})
    
    return TokenResponse(
        token=token,
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role.value,
            created_at=user.created_at.isoformat()
        )
    )

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login user"""
    
    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    token = create_access_token(data={"sub": user.id})
    
    return TokenResponse(
        token=token,
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role.value,
            created_at=user.created_at.isoformat()
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role.value,
        created_at=current_user.created_at.isoformat()
    )
