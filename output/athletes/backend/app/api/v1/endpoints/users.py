"""User Profile API endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.models import Users
from app.schemas.schemas import UserResponse, UserUpdate, SuccessResponse

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: Users = Depends(get_current_user)):
    """Get current user profile."""
    return current_user

@router.patch("/me", response_model=SuccessResponse)
async def update_user_profile(user_update: UserUpdate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    """Update current user profile."""
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    return SuccessResponse(success=True)
