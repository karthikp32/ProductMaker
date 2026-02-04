import logging
import os
import secrets
import time
from typing import Optional, Dict, Any

import httpx
import stripe
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from infrastructure.event_bus import EventBus
from core.orchestrator import Orchestrator
from agents.pm_agent import PMAgent
from agents.architect_agent import ArchitectAgent
from agents.frontend_agent import FrontendAgent
from agents.backend_agent import BackendAgent
from agents.marketing_agent import MarketingAgent
from agents.sales_agent import SalesAgent
from agents.analytics_agent import AnalyticsAgent

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ProductMaker API")

# CORS for local dev + configurable frontend
frontend_base_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
allowed_origins = os.getenv("CORS_ALLOWED_ORIGINS", frontend_base_url).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize System
event_bus = EventBus()
orchestrator = Orchestrator(event_bus)

# Initialize Agents
pm_agent = PMAgent("pm", event_bus)
agents = {
    "pm": pm_agent,
    "architect": ArchitectAgent("architect", event_bus),
    "frontend": FrontendAgent("frontend", event_bus),
    "backend": BackendAgent("backend", event_bus),
    "marketing": MarketingAgent("marketing", event_bus),
    "sales": SalesAgent("sales", event_bus),
    "analytics": AnalyticsAgent("analytics", event_bus),
}

# Start Orchestrator
orchestrator.start()

class InstructionRequest(BaseModel):
    instruction: str
    context: Optional[Dict[str, Any]] = {}

class SegmentAnalysisRequest(BaseModel):
    segment_name: str
    industry: str
    target_repo_path: Optional[str] = None

class IndustryAnalysisRequest(BaseModel):
    industry: str
    target_repo_path: Optional[str] = None

class DeployRequest(BaseModel):
    desired_url: Optional[str] = None

# OAuth + billing configuration
OAUTH_CONFIG = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://openidconnect.googleapis.com/v1/userinfo",
        "scope": "openid email profile",
    },
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID", ""),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
        "auth_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "emails_url": "https://api.github.com/user/emails",
        "scope": "read:user user:email",
    },
}

FREE_USAGE_LIMIT = int(os.getenv("FREE_USAGE_LIMIT", "5"))
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", str(60 * 60 * 24)))

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")
STRIPE_SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", f"{frontend_base_url}/success")
STRIPE_CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", f"{frontend_base_url}/billing")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# In-memory session and state store (replace with DB in production)
sessions: Dict[str, Dict[str, Any]] = {}
oauth_states: Dict[str, Dict[str, Any]] = {}

@app.post("/instruct/{agent_name}")
async def instruct_agent(agent_name: str, request: InstructionRequest):
    agent_name = agent_name.lower()
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found.")
    
    event_type = f"INSTRUCT_{agent_name.upper()}"
    payload = {
        "instruction": request.instruction,
        "context": request.context
    }
    
    logger.info(f"API: Instructing {agent_name} with: {request.instruction}")
    event_bus.publish(event_type, payload)
    
    return {"status": "Instruction sent", "agent": agent_name}

@app.post("/analyze-segment")
async def analyze_segment(request: SegmentAnalysisRequest, background_tasks: BackgroundTasks):
    logger.info(f"API: Requesting analysis for segment: {request.segment_name}")
    background_tasks.add_task(pm_agent.analyze_segment, request.dict())
    return {"status": "Analysis started in background", "segment": request.segment_name}

@app.post("/analyze-industry")
async def analyze_industry(request: IndustryAnalysisRequest, background_tasks: BackgroundTasks):
    logger.info(f"API: Requesting industry analysis for: {request.industry}")
    background_tasks.add_task(pm_agent.analyze_industry, request.dict())
    return {"status": "Industry analysis started in background", "industry": request.industry}

@app.get("/agents")
async def list_agents():
    return {"agents": list(agents.keys())}

def _cleanup_sessions() -> None:
    now = time.time()
    expired = [token for token, data in sessions.items() if data["expires_at"] < now]
    for token in expired:
        sessions.pop(token, None)

def _get_bearer_token(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    return None

def get_current_user(request: Request) -> Dict[str, Any]:
    _cleanup_sessions()
    token = _get_bearer_token(request)
    if not token or token not in sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return sessions[token]

@app.get("/auth/login/{provider}")
async def oauth_login(provider: str):
    provider = provider.lower()
    if provider not in OAUTH_CONFIG:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    config = OAUTH_CONFIG[provider]
    if not config["client_id"]:
        raise HTTPException(status_code=500, detail="OAuth client not configured")

    state = secrets.token_urlsafe(16)
    oauth_states[state] = {"provider": provider, "created_at": time.time()}
    params = {
        "client_id": config["client_id"],
        "redirect_uri": f"{os.getenv('OAUTH_REDIRECT_BASE', 'http://localhost:8080')}/auth/callback/{provider}",
        "response_type": "code",
        "scope": config["scope"],
        "state": state,
    }
    if provider == "github":
        params.pop("response_type", None)

    auth_url = httpx.URL(config["auth_url"]).copy_add_params(params)
    return RedirectResponse(url=str(auth_url))

@app.get("/auth/callback/{provider}")
async def oauth_callback(provider: str, code: Optional[str] = None, state: Optional[str] = None):
    provider = provider.lower()
    if provider not in OAUTH_CONFIG:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")
    if state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state")

    oauth_states.pop(state, None)
    config = OAUTH_CONFIG[provider]
    redirect_uri = f"{os.getenv('OAUTH_REDIRECT_BASE', 'http://localhost:8080')}/auth/callback/{provider}"

    async with httpx.AsyncClient() as client:
        if provider == "google":
            token_res = await client.post(
                config["token_url"],
                data={
                    "code": code,
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
                headers={"Accept": "application/json"},
            )
            token_res.raise_for_status()
            token_payload = token_res.json()
            access_token = token_payload.get("access_token")
            user_res = await client.get(
                config["userinfo_url"],
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_res.raise_for_status()
            user_payload = user_res.json()
            name = user_payload.get("name") or user_payload.get("given_name") or "Google User"
            email = user_payload.get("email")
        else:
            token_res = await client.post(
                config["token_url"],
                data={
                    "code": code,
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"],
                    "redirect_uri": redirect_uri,
                    "state": state,
                },
                headers={"Accept": "application/json"},
            )
            token_res.raise_for_status()
            token_payload = token_res.json()
            access_token = token_payload.get("access_token")
            user_res = await client.get(
                config["userinfo_url"],
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_res.raise_for_status()
            user_payload = user_res.json()
            name = user_payload.get("name") or user_payload.get("login") or "GitHub User"
            email = user_payload.get("email")
            if not email:
                emails_res = await client.get(
                    config["emails_url"],
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if emails_res.status_code == 200:
                    emails = emails_res.json()
                    primary = next((item for item in emails if item.get("primary")), None)
                    email = (primary or emails[0]).get("email") if emails else None

    token = secrets.token_urlsafe(24)
    sessions[token] = {
        "id": secrets.token_hex(8),
        "name": name,
        "email": email,
        "provider": provider,
        "paid": False,
        "remaining": FREE_USAGE_LIMIT,
        "created_at": time.time(),
        "expires_at": time.time() + SESSION_TTL_SECONDS,
    }

    return RedirectResponse(url=f"{frontend_base_url}/?token={token}")

@app.get("/auth/me")
async def auth_me(user: Dict[str, Any] = Depends(get_current_user)):
    return {"user": user}

@app.post("/usage/consume")
async def consume_usage(user: Dict[str, Any] = Depends(get_current_user)):
    if not user["paid"]:
        if user["remaining"] <= 0:
            raise HTTPException(status_code=402, detail="Free usage limit reached")
        user["remaining"] -= 1
    return {"paid": user["paid"], "remaining": user["remaining"]}

@app.post("/billing/checkout")
async def create_checkout(user: Dict[str, Any] = Depends(get_current_user)):
    if not stripe.api_key or not STRIPE_PRICE_ID:
        raise HTTPException(status_code=500, detail="Stripe is not configured")

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
        success_url=STRIPE_SUCCESS_URL,
        cancel_url=STRIPE_CANCEL_URL,
        client_reference_id=user["id"],
        metadata={"user_id": user["id"]},
    )
    return {"id": session.id, "url": session.url}

@app.post("/billing/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = None

    if STRIPE_WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
    else:
        payload_json = await request.json()
        event = stripe.Event.construct_from(payload_json, stripe.api_key)

    if event["type"] == "checkout.session.completed":
        session_obj = event["data"]["object"]
        user_id = session_obj.get("client_reference_id")
        for token, data in sessions.items():
            if data["id"] == user_id:
                data["paid"] = True
                data["remaining"] = FREE_USAGE_LIMIT
                break
    return {"status": "ok"}

@app.post("/deploy")
async def deploy_site(request: DeployRequest, user: Dict[str, Any] = Depends(get_current_user)):
    desired = request.desired_url.strip() if request.desired_url else ""
    if not desired:
        desired = f"productmaker.com/{secrets.token_urlsafe(6)}"
    return {"status": "deployed", "url": desired}
