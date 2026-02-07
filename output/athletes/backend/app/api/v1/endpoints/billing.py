"""Stripe Billing API endpoints."""
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db, get_current_user
from app.models.models import Users, Subscriptions
from app.schemas.schemas import CheckoutRequest, CheckoutResponse, SubscriptionResponse

router = APIRouter()
stripe.api_key = settings.STRIPE_SECRET_KEY
PRICE_MAP = {"pro": settings.STRIPE_PRICE_PRO, "premium": settings.STRIPE_PRICE_PREMIUM}

@router.post("/create-checkout", response_model=CheckoutResponse)
async def create_checkout_session(checkout_data: CheckoutRequest, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    """Create a Stripe checkout session for subscription."""
    try:
        price_id = PRICE_MAP.get(checkout_data.plan)
        if not price_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid plan: {checkout_data.plan}")
        
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(email=current_user.email, metadata={"user_id": str(current_user.id)})
            current_user.stripe_customer_id = customer.id
            db.commit()
        
        session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            success_url=f"{settings.FRONTEND_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/billing/cancel"
        )
        return CheckoutResponse(checkout_url=session.url)
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhooks."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook")
    
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user = db.query(Users).filter(Users.stripe_customer_id == session.get("customer")).first()
        if user:
            user.subscription_tier = "pro"
            db.commit()
    return {"received": True}

@router.get("/subscription", response_model=SubscriptionResponse | None)
async def get_subscription(db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    """Get current user's subscription."""
    return db.query(Subscriptions).filter(Subscriptions.user_id == current_user.id, Subscriptions.status == "active").first()
