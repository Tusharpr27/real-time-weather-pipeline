"""
Authentication Routes
Handles user login, registration, and authentication
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import jwt
import bcrypt

from config import settings
from src.database.database import get_db
from src.database.models import User
from src.utils.logger import logger

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Pydantic schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "secure_password_123",
                "full_name": "John Doe"
            }
        }


class UserLogin(BaseModel):
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "secure_password_123"
            }
        }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    email_verified: bool
    theme_preference: str
    notifications_enabled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    message: str
    success: bool = True


# Utility functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(hours=24)
    
    expire = datetime.utcnow() + expires_delta
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm="HS256"
    )
    return token


def decode_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return {"user_id": int(user_id)}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from token"""
    payload = decode_token(token)
    user_id = payload.get("user_id")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    return user


# Routes

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **email**: User email (must be unique)
    - **password**: User password (minimum 8 characters)
    - **full_name**: Optional full name
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password
        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            is_active=True,
            email_verified=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user registered: {user_data.email}")
        
        # Create token
        access_token = create_access_token(new_user.id)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=86400,
            user={
                "id": new_user.id,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "is_admin": new_user.is_admin
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password
    
    - **email**: User email
    - **password**: User password
    """
    try:
        # Find user
        user = db.query(User).filter(User.email == credentials.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        logger.info(f"User logged in: {credentials.email}")
        
        # Create token
        access_token = create_access_token(user.id)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=86400,
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_admin": user.is_admin
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile
    """
    return UserResponse.from_orm(current_user)


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout (invalidate current token)
    Note: In a real app, you'd add token to blacklist
    """
    logger.info(f"User logged out: {current_user.email}")
    return MessageResponse(message="Logged out successfully")


@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Refresh access token
    """
    access_token = create_access_token(current_user.id)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400,
        user={
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "is_admin": current_user.is_admin
        }
    )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    try:
        # Verify old password
        if not verify_password(old_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters long"
            )
        
        # Update password
        current_user.hashed_password = hash_password(new_password)
        db.commit()
        
        logger.info(f"User changed password: {current_user.email}")
        
        return MessageResponse(message="Password changed successfully")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )
