from fastapi import APIRouter

from app.api.v1.endpoints import sessions, metrics, users, dashboard, auth, insights, billing

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(dashboard.router, prefix="/stats/dashboard", tags=["dashboard"])
api_router.include_router(insights.router, prefix="/insights", tags=["insights"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
