"""Dependency injection for FastAPI."""
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from supabase import create_client, Client

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.models import Users

security = HTTPBearer()

def get_db() -> Generator:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_supabase() -> Client:
    """Get Supabase client."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase),
    db: Session = Depends(get_db)
) -> Users:
    """Validate JWT and return current user."""
    try:
        user_response = supabase.auth.get_user(credentials.credentials)
        if user_response.user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        user = db.query(Users).filter(Users.id == user_response.user.id).first()
        if not user:
            user = Users(
                id=user_response.user.id,
                email=user_response.user.email,
                full_name=user_response.user.user_metadata.get("full_name", ""),
                sport=user_response.user.user_metadata.get("sport")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
