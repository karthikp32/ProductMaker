"""Dashboard Statistics API endpoints."""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_db, get_current_user
from app.models.models import TrainingSessions, PerformanceMetrics, Users
from app.schemas.schemas import DashboardStatsResponse

router = APIRouter()

@router.get("", response_model=DashboardStatsResponse)
async def get_dashboard_stats(db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    """Get dashboard statistics for the current user."""
    total_sessions = db.query(func.count(TrainingSessions.id)).filter(TrainingSessions.user_id == current_user.id).scalar() or 0
    
    week_start = datetime.utcnow() - timedelta(days=7)
    this_week = db.query(func.count(TrainingSessions.id)).filter(
        TrainingSessions.user_id == current_user.id, TrainingSessions.created_at >= week_start
    ).scalar() or 0
    
    total_minutes = db.query(func.sum(TrainingSessions.duration_minutes)).filter(TrainingSessions.user_id == current_user.id).scalar() or 0
    recent_metrics = db.query(PerformanceMetrics).filter(PerformanceMetrics.user_id == current_user.id).order_by(PerformanceMetrics.recorded_at.desc()).limit(5).all()
    
    last_week = db.query(func.count(TrainingSessions.id)).filter(
        TrainingSessions.user_id == current_user.id,
        TrainingSessions.created_at >= week_start - timedelta(days=7),
        TrainingSessions.created_at < week_start
    ).scalar() or 0
    
    trend = "improving" if this_week > last_week else ("declining" if this_week < last_week else "stable")
    
    return DashboardStatsResponse(
        total_sessions=total_sessions, this_week_sessions=this_week,
        total_training_minutes=total_minutes, recent_metrics=recent_metrics, performance_trend=trend
    )
