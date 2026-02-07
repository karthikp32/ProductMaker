"""Performance Metrics API endpoints."""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.models import PerformanceMetrics, Users
from app.schemas.schemas import MetricCreate, MetricResponse, MetricListResponse

router = APIRouter()

@router.get("", response_model=MetricListResponse)
async def list_metrics(
    metric_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """List performance metrics for the current user."""
    query = db.query(PerformanceMetrics).filter(PerformanceMetrics.user_id == current_user.id)
    if metric_type:
        query = query.filter(PerformanceMetrics.metric_type == metric_type)
    if start_date:
        query = query.filter(PerformanceMetrics.recorded_at >= start_date)
    if end_date:
        query = query.filter(PerformanceMetrics.recorded_at <= end_date)
    return MetricListResponse(metrics=query.order_by(PerformanceMetrics.recorded_at.desc()).all())

@router.post("", response_model=MetricResponse)
async def create_metric(metric_data: MetricCreate, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    """Record a new performance metric."""
    metric = PerformanceMetrics(
        user_id=current_user.id,
        metric_type=metric_data.metric_type,
        value=metric_data.value,
        unit=metric_data.unit
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric
