"""AI Insights API endpoints using OpenAI."""
import openai
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db, get_current_user
from app.models.models import Users, AiInsights, TrainingSessions, PerformanceMetrics
from app.schemas.schemas import InsightRequest, InsightResponse, InsightListResponse

router = APIRouter()
openai.api_key = settings.OPENAI_API_KEY

PROMPTS = {
    "training_advice": "Analyze training sessions and provide actionable advice for improvement.",
    "recovery": "Based on training intensity, suggest optimal recovery strategies.",
    "nutrition": "Given training load, recommend nutrition adjustments."
}

@router.get("", response_model=InsightListResponse)
async def list_insights(db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    """List AI-generated insights for the current user."""
    insights = db.query(AiInsights).filter(AiInsights.user_id == current_user.id).order_by(AiInsights.created_at.desc()).limit(10).all()
    return InsightListResponse(insights=insights)

@router.post("/generate", response_model=InsightResponse)
async def generate_insight(request: InsightRequest, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    """Generate a new AI insight based on recent training data."""
    if current_user.subscription_tier == "free":
        raise HTTPException(status_code=403, detail="AI insights require a Pro or Premium subscription")
    
    sessions = db.query(TrainingSessions).filter(TrainingSessions.user_id == current_user.id).order_by(TrainingSessions.session_date.desc()).limit(10).all()
    session_summary = "\n".join([f"- {s.session_date}: {s.sport_type}, {s.duration_minutes}min" for s in sessions]) or "No sessions"
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert sports performance coach."},
                {"role": "user", "content": f"Recent training:\n{session_summary}\n\n{PROMPTS.get(request.insight_type, PROMPTS['training_advice'])}"}
            ],
            max_tokens=500
        )
        content = response.choices[0].message.content.strip()
    except Exception as e:
        content = f"Unable to generate insight: {str(e)}"
    
    insight = AiInsights(user_id=current_user.id, insight_type=request.insight_type, content=content, context={"sessions": len(sessions)})
    db.add(insight)
    db.commit()
    db.refresh(insight)
    return insight
