from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.controllers import register_user, login_user
from src.auth.models import UserCreate, UserResponse, Token
from src.auth.services import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

# In src/auth/routes.py, modify the signup route:
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """Register a new user."""
    try:
        return await register_user(user_data)
    except Exception as e:
        # Log the error for debugging
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login a user."""
    return await login_user(form_data)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    """Get current logged-in user details."""
    return current_user