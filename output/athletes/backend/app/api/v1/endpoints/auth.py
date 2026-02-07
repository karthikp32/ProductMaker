"""Authentication endpoints using Supabase Auth."""
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.core.deps import get_supabase
from app.schemas.schemas import UserCreate, UserLogin, TokenResponse

router = APIRouter()

@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserCreate, supabase: Client = Depends(get_supabase)):
    """Register a new user."""
    try:
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {"data": {"full_name": user_data.full_name, "sport": user_data.sport}}
        })
        if auth_response.user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create user")
        return TokenResponse(access_token=auth_response.session.access_token, refresh_token=auth_response.session.refresh_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, supabase: Client = Depends(get_supabase)):
    """Authenticate user and return tokens."""
    try:
        auth_response = supabase.auth.sign_in_with_password({"email": credentials.email, "password": credentials.password})
        if auth_response.session is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return TokenResponse(access_token=auth_response.session.access_token, refresh_token=auth_response.session.refresh_token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
