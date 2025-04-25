from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta

from src.auth.services import (
    get_user_by_email,
    get_user_by_username,
    get_password_hash,
    verify_password,
    create_access_token,
)
from src.auth.models import UserCreate, Token, UserResponse
from src.database.connection import prisma
from src.config.settings import JWT_EXPIRATION_TIME_MINUTES

async def register_user(user_data: UserCreate):
    """Register a new user."""
    # Check if email already exists
    db_user_email = await get_user_by_email(user_data.email)
    if db_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if username already exists
    db_user_username = await get_user_by_username(user_data.username)
    if db_user_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict()
    user_dict.update({"password": hashed_password})
    
    # Save to database
    new_user = await prisma.user.create(data=user_dict)
    
    # Return the user without password
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
    )

async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate and login a user."""
    # Try to find user by username
    user = await get_user_by_username(form_data.username)
    
    # If not found, try email (since form_data.username could be an email)
    if not user:
        user = await get_user_by_email(form_data.username)
    
    # If still not found or password doesn't match
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")