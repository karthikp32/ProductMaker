"""Training Sessions API endpoints."""
from datetime import date
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.models import TrainingSessions, Users
from app.schemas.schemas import SessionCreate, SessionResponse, SessionListResponse, SuccessResponse

router = APIRouter()

@router.get("", response_model=SessionListResponse)
async def list_sessions(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """List training sessions for the current user."""
    query = db.query(TrainingSessions).filter(TrainingSessions.user_id == current_user.id)
    if start_date:
        query = query.filter(TrainingSessions.session_date >= start_date)
    if end_date:
        query = query.filter(TrainingSessions.session_date <= end_date)
    sessions = query.order_by(TrainingSessions.session_date.desc()).limit(limit).all()
    return SessionListResponse(sessions=sessions)

@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Create a new training session."""
    session = TrainingSessions(
        user_id=current_user.id,
        session_date=session_data.session_date,
        sport_type=session_data.sport_type,
        duration_minutes=session_data.duration_minutes,
        intensity=session_data.intensity,
        notes=session_data.notes,
        metrics=session_data.metrics or {}
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: UUID, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    """Get a specific training session."""
    session = db.query(TrainingSessions).filter(
        TrainingSessions.id == session_id, TrainingSessions.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.delete("/{session_id}", response_model=SuccessResponse)
async def delete_session(session_id: UUID, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    """Delete a training session."""
    session = db.query(TrainingSessions).filter(
        TrainingSessions.id == session_id, TrainingSessions.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return SuccessResponse(success=True)
