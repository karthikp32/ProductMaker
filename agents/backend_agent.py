"""
Backend SWE Agent: Owns the "Logic"

A highly skilled backend engineer agent inspired by the exceptional technical abilities
of Jeff Dean (distributed systems mastery), Linus Torvalds (systems programming excellence),
and John Carmack (performance optimization genius).

Responsibilities:
- Implements API handlers and business logic
- Sets up database migrations (Supabase)
- Conditionally integrates 3rd party APIs based on system design

Tools: write_code, run_tests, db_migrate, create_pr
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional, Set
from core.base_agent import BaseAgent
from infrastructure.event_bus import EventBus
from infrastructure.llm.reasoning_model_client import ReasoningModelClient

logger = logging.getLogger(__name__)


class BackendAgent(BaseAgent):
    """
    Backend SWE Agent: Expert-level backend code generation.
    
    Philosophy:
    - Performance first: O(1) lookups, efficient queries, connection pooling
    - Security always: Input validation, SQL injection prevention, auth middleware
    - Clean architecture: Separation of concerns, dependency injection
    - Test everything: Unit tests, integration tests, edge cases
    - Minimal footprint: Only generate code for required integrations
    """
    
    def __init__(self, name: str, event_bus: EventBus):
        super().__init__(name, event_bus)
        self.reasoning_client = ReasoningModelClient()
        self._enabled_integrations: Set[str] = set()
    
    @property
    def role(self) -> str:
        return "Senior Backend Engineer: Expert in API design, database optimization, and system integration."

    @property
    def functions(self) -> list:
        return []

    def setup_subscriptions(self):
        self.event_bus.subscribe("ARCHITECTURE_APPROVED", self.on_architecture_approved)
        self.event_bus.subscribe("DESIGN_COMPLETED", self.on_design_completed)

    def handle_instruction(self, instruction: str, context: Dict[str, Any]):
        """Handles explicit instructions to build backend."""
        if "build" in instruction.lower() and "industry" in context:
            self.generate_code_from_designs(context["industry"])

    def on_architecture_approved(self, payload: Any):
        logger.info("Backend Agent: Architecture approved. Building backend...")
        industry = payload.get("industry", "default")
        self.generate_code_from_designs(industry)

    def on_design_completed(self, payload: Any):
        industry = payload.get("industry")
        if industry:
            logger.info(f"Backend Agent: Design completed for '{industry}'. Ready for architecture.")

    def _detect_enabled_integrations(self, design: Dict[str, Any]) -> Set[str]:
        """
        Detect which integrations are enabled based on the system design.
        Checks high_level_design.integrations, functional_requirements, and api_endpoints.
        """
        enabled = set()
        
        # Check high_level_design.integrations
        hld = design.get("high_level_design", {})
        integrations = hld.get("integrations", {})
        for name, config in integrations.items():
            if isinstance(config, dict) and config.get("enabled", False):
                enabled.add(name.lower())
            elif config is True:
                enabled.add(name.lower())
        
        # Check functional_requirements for integration_required
        for fr in design.get("functional_requirements", []):
            if fr.get("integration_required"):
                enabled.add(fr["integration_required"].lower())
        
        # Check api_endpoints for conditions
        for endpoint in design.get("api_endpoints", []):
            if endpoint.get("condition"):
                enabled.add(endpoint["condition"].lower())
        
        # Backward compatibility: check old format
        old_integrations = design.get("integrations", {})
        if "payments" in old_integrations:
            enabled.add("stripe")
        if "ai" in old_integrations:
            enabled.add("openai")
        
        logger.info(f"Backend Agent: Enabled integrations: {enabled}")
        return enabled

    def _get_project_name(self, design: Dict[str, Any]) -> str:
        """Extract project name from design."""
        # New format
        if "product_idea" in design:
            return design["product_idea"].get("title", "backend").split(" - ")[0]
        # Old format
        return design.get("project_name", "backend")

    def _get_description(self, design: Dict[str, Any]) -> str:
        """Extract description from design."""
        if "product_idea" in design:
            return design["product_idea"].get("description", "FastAPI Backend")
        return design.get("description", "FastAPI Backend")

    def _get_entities(self, design: Dict[str, Any]) -> List[Dict]:
        """Get entities/tables from design, supporting both formats."""
        # New format: core_entities
        if "core_entities" in design:
            entities = []
            for entity in design["core_entities"]:
                # Filter out entities with conditions that aren't enabled
                condition = entity.get("condition")
                if condition and condition.lower() not in self._enabled_integrations:
                    continue
                # Convert to table format
                entities.append({
                    "name": entity["name"],
                    "description": entity.get("description", ""),
                    "columns": [
                        {
                            "name": attr["name"],
                            "type": attr["type"],
                            "constraints": attr.get("constraints", [])
                        }
                        for attr in entity.get("attributes", [])
                    ]
                })
            return entities
        
        # Old format: database_schema.tables
        return design.get("database_schema", {}).get("tables", [])

    def _get_supabase_config(self, design: Dict[str, Any]) -> Dict:
        """Get Supabase config from design."""
        if "high_level_design" in design:
            return design["high_level_design"].get("supabase_config", {})
        return design.get("supabase_config", {})

    def generate_code_from_designs(self, industry: str):
        """
        Main entry point: reads system_design.json and generates backend.
        Only generates integrations that are specified in the design.
        """
        safe_industry = industry.replace(" ", "_").lower()
        design_dir = os.path.abspath(f"output/{safe_industry}/designs")
        output_dir = os.path.abspath(f"output/{safe_industry}/backend")

        # Load system design
        design_file = os.path.join(design_dir, "system_design.json")
        if not os.path.exists(design_file):
            logger.error(f"Backend Agent: System design not found: {design_file}")
            print(f"Error: system_design.json not found in {design_dir}")
            return

        with open(design_file, 'r') as f:
            system_design = json.load(f)

        # Detect which integrations are enabled
        self._enabled_integrations = self._detect_enabled_integrations(system_design)
        
        project_name = self._get_project_name(system_design)
        logger.info(f"Backend Agent: Loaded system design for '{project_name}'")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Generate all backend components
        print(f"Generating backend for {industry}...")
        
        self._create_project_structure(output_dir, system_design)
        self._generate_database_migrations(output_dir, system_design)
        self._generate_models(output_dir, system_design)
        self._generate_schemas(output_dir, system_design)
        self._generate_api_handlers(output_dir, system_design)
        self._generate_auth(output_dir, system_design)
        
        # Conditionally generate integrations
        if "stripe" in self._enabled_integrations:
            self._generate_stripe_integration(output_dir, system_design)
        else:
            logger.info("Backend Agent: Skipping Stripe (not in design)")
            
        if "openai" in self._enabled_integrations:
            self._generate_openai_integration(output_dir, system_design)
        else:
            logger.info("Backend Agent: Skipping OpenAI (not in design)")
        
        self._generate_main_app(output_dir, system_design)
        self._generate_config(output_dir, system_design)
        self._generate_tests(output_dir, system_design)

        print(f"Backend successfully built in {output_dir}")
        
        self.publish_event("BACKEND_BUILT", {
            "industry": industry,
            "output_dir": output_dir,
            "status": "success",
            "integrations": list(self._enabled_integrations)
        })

    def _create_project_structure(self, output_dir: str, design: Dict[str, Any]):
        """Creates FastAPI project scaffolding."""
        project_name = self._get_project_name(design).lower().replace(" ", "_").replace("-", "_")
        description = self._get_description(design)
        
        # Directory structure
        dirs = [
            "app", "app/api", "app/api/v1", "app/api/v1/endpoints",
            "app/core", "app/db", "app/models", "app/schemas",
            "app/services", "app/integrations",
            "migrations", "tests", "tests/api", "tests/services"
        ]
        
        for d in dirs:
            os.makedirs(os.path.join(output_dir, d), exist_ok=True)
            if d.startswith("app") or d.startswith("tests"):
                init_file = os.path.join(output_dir, d, "__init__.py")
                if not os.path.exists(init_file):
                    self._write_file(output_dir, f"{d}/__init__.py", "")

        # Build requirements based on enabled integrations
        requirements_lines = [
            "# Core",
            "fastapi>=0.109.0",
            "uvicorn[standard]>=0.27.0",
            "python-dotenv>=1.0.0",
            "pydantic>=2.5.0",
            "pydantic-settings>=2.1.0",
            "",
            "# Database",
            "supabase>=2.3.0",
            "sqlalchemy>=2.0.0",
            "asyncpg>=0.29.0",
            "alembic>=1.13.0",
            "",
            "# Authentication",
            "python-jose[cryptography]>=3.3.0",
            "passlib[bcrypt]>=1.7.4",
            "",
            "# HTTP Client",
            "httpx>=0.26.0",
            "",
            "# Testing",
            "pytest>=7.4.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
            "",
            "# Utilities",
            "python-multipart>=0.0.6",
        ]
        
        if "stripe" in self._enabled_integrations:
            requirements_lines.insert(-3, "")
            requirements_lines.insert(-3, "# Payments")
            requirements_lines.insert(-3, "stripe>=7.0.0")
        
        if "openai" in self._enabled_integrations:
            requirements_lines.insert(-3, "")
            requirements_lines.insert(-3, "# AI")
            requirements_lines.insert(-3, "openai>=1.10.0")
        
        self._write_file(output_dir, "requirements.txt", "\n".join(requirements_lines))

        # pyproject.toml
        pyproject = f'''[project]
name = "{project_name}"
version = "0.1.0"
description = "{description}"
requires-python = ">=3.11"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"
'''
        self._write_file(output_dir, "pyproject.toml", pyproject)

        # .env.example - only include needed vars
        env_lines = [
            "# Supabase",
            "SUPABASE_URL=https://your-project.supabase.co",
            "SUPABASE_ANON_KEY=your-anon-key",
            "SUPABASE_SERVICE_ROLE_KEY=your-service-role-key",
            "DATABASE_URL=postgresql://postgres:password@db.your-project.supabase.co:5432/postgres",
            "",
        ]
        
        if "stripe" in self._enabled_integrations:
            env_lines.extend([
                "# Stripe",
                "STRIPE_SECRET_KEY=sk_test_xxx",
                "STRIPE_WEBHOOK_SECRET=whsec_xxx",
                "STRIPE_PRICE_PRO=price_xxx",
                "STRIPE_PRICE_PREMIUM=price_xxx",
                "",
            ])
        
        if "openai" in self._enabled_integrations:
            env_lines.extend([
                "# OpenAI",
                "OPENAI_API_KEY=sk-xxx",
                "",
            ])
        
        env_lines.extend([
            "# App",
            "SECRET_KEY=your-super-secret-key-change-in-production",
            "ENVIRONMENT=development",
        ])
        
        self._write_file(output_dir, ".env.example", "\n".join(env_lines))

        # .gitignore
        gitignore = """__pycache__/
*.py[cod]
*$py.class
.env
.venv/
venv/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
"""
        self._write_file(output_dir, ".gitignore", gitignore)

        logger.info("Backend Agent: Project structure created.")

    def _generate_database_migrations(self, output_dir: str, design: Dict[str, Any]):
        """Generates Supabase-compatible SQL migrations."""
        tables = self._get_entities(design)
        supabase_config = self._get_supabase_config(design)

        if not tables:
            logger.warning("Backend Agent: No database tables defined in design.")
            return

        migration_lines = [
            "-- Migration: Initial Schema",
            "-- Generated by Backend Agent",
            "-- Supabase-compatible PostgreSQL",
            "",
            '-- Enable UUID extension',
            'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',
            "",
        ]

        for table in tables:
            table_name = table.get("name")
            columns = table.get("columns", [])
            description = table.get("description", "")

            migration_lines.append(f"-- {description}")
            migration_lines.append(f"CREATE TABLE IF NOT EXISTS {table_name} (")

            col_defs = []
            for col in columns:
                col_name = col.get("name")
                col_type = col.get("type")
                constraints = col.get("constraints", [])
                constraint_str = " ".join(constraints) if constraints else ""
                col_defs.append(f"    {col_name} {col_type} {constraint_str}".strip())

            migration_lines.append(",\n".join(col_defs))
            migration_lines.append(");")
            migration_lines.append("")

        # Row Level Security
        if supabase_config.get("row_level_security"):
            migration_lines.append("-- Enable Row Level Security")
            for table in tables:
                table_name = table.get("name")
                migration_lines.append(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;")
            migration_lines.append("")

            user_tables = [t["name"] for t in tables if any(
                c["name"] == "user_id" for c in t.get("columns", [])
            )]
            
            for table_name in user_tables:
                migration_lines.extend([
                    f"-- RLS Policy for {table_name}",
                    f'CREATE POLICY "Users can view own {table_name}"',
                    f"    ON {table_name} FOR SELECT USING (auth.uid() = user_id);",
                    f'CREATE POLICY "Users can insert own {table_name}"',
                    f"    ON {table_name} FOR INSERT WITH CHECK (auth.uid() = user_id);",
                    f'CREATE POLICY "Users can update own {table_name}"',
                    f"    ON {table_name} FOR UPDATE USING (auth.uid() = user_id);",
                    f'CREATE POLICY "Users can delete own {table_name}"',
                    f"    ON {table_name} FOR DELETE USING (auth.uid() = user_id);",
                    ""
                ])

        # Performance Indexes
        migration_lines.append("-- Performance Indexes")
        for table in tables:
            table_name = table.get("name")
            columns = table.get("columns", [])
            
            if any(c["name"] == "user_id" for c in columns):
                migration_lines.append(
                    f"CREATE INDEX IF NOT EXISTS idx_{table_name}_user_id ON {table_name}(user_id);"
                )
            if any(c["name"] == "created_at" for c in columns):
                migration_lines.append(
                    f"CREATE INDEX IF NOT EXISTS idx_{table_name}_created_at ON {table_name}(created_at DESC);"
                )

        self._write_file(output_dir, "migrations/001_initial_schema.sql", "\n".join(migration_lines))
        logger.info("Backend Agent: Database migrations generated.")

    def _generate_models(self, output_dir: str, design: Dict[str, Any]):
        """Generates SQLAlchemy models."""
        tables = self._get_entities(design)

        type_map = {
            "UUID": "PGUUID(as_uuid=True)", "TEXT": "String", "VARCHAR": "String",
            "INTEGER": "Integer", "INT": "Integer", "NUMERIC": "Numeric",
            "BOOLEAN": "Boolean", "TIMESTAMP": "DateTime", "DATE": "Date",
            "JSONB": "JSON", "JSON": "JSON"
        }

        model_imports = '''"""SQLAlchemy models. Generated by Backend Agent."""
from datetime import datetime, date
from typing import Optional, Any
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, Date, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass

'''
        models_code = [model_imports]

        for table in tables:
            table_name = table.get("name")
            class_name = "".join(word.capitalize() for word in table_name.split("_"))
            columns = table.get("columns", [])
            description = table.get("description", "")

            models_code.append(f'class {class_name}(Base):')
            models_code.append(f'    """{description}"""')
            models_code.append(f'    __tablename__ = "{table_name}"')
            models_code.append("")

            for col in columns:
                col_name = col.get("name")
                col_type = col.get("type", "TEXT").upper().split("(")[0]
                constraints = col.get("constraints", [])

                sa_type = type_map.get(col_type, "String")
                col_args = ["PGUUID(as_uuid=True)" if col_type == "UUID" else sa_type]

                for constraint in constraints:
                    if "PRIMARY KEY" in constraint:
                        col_args.append("primary_key=True")
                    if "REFERENCES" in constraint:
                        ref = constraint.replace("REFERENCES ", "").replace("(", ".").replace(")", "")
                        col_args.append(f'ForeignKey("{ref}")')
                    if "NOT NULL" in constraint:
                        col_args.append("nullable=False")
                    if "UNIQUE" in constraint:
                        col_args.append("unique=True")
                    if "DEFAULT" in constraint:
                        if "gen_random_uuid()" in constraint:
                            col_args.append("default=uuid4")
                        elif "NOW()" in constraint:
                            col_args.append("default=datetime.utcnow")

                models_code.append(f"    {col_name} = Column({', '.join(col_args)})")

            models_code.append("")
            models_code.append("")

        self._write_file(output_dir, "app/models/models.py", "\n".join(models_code))
        logger.info("Backend Agent: SQLAlchemy models generated.")

    def _generate_schemas(self, output_dir: str, design: Dict[str, Any]):
        """Generates Pydantic schemas."""
        schemas_code = '''"""Pydantic schemas for request/response validation. Generated by Backend Agent."""
from datetime import datetime, date
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# ==================== Auth ====================
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    sport: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    sport: Optional[str]
    subscription_tier: str
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    sport: Optional[str] = None


# ==================== Sessions ====================
class SessionCreate(BaseModel):
    session_date: date
    sport_type: str
    duration_minutes: int = Field(..., gt=0)
    intensity: Optional[str] = None
    notes: Optional[str] = None
    metrics: Optional[dict] = None

class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    session_date: date
    sport_type: str
    duration_minutes: int
    intensity: Optional[str]
    notes: Optional[str]
    metrics: Optional[dict]
    created_at: datetime
    class Config:
        from_attributes = True

class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]


# ==================== Metrics ====================
class MetricCreate(BaseModel):
    metric_type: str
    value: float
    unit: Optional[str] = None

class MetricResponse(BaseModel):
    id: UUID
    user_id: UUID
    metric_type: str
    value: float
    unit: Optional[str]
    recorded_at: datetime
    class Config:
        from_attributes = True

class MetricListResponse(BaseModel):
    metrics: List[MetricResponse]


# ==================== Dashboard ====================
class DashboardStatsResponse(BaseModel):
    total_sessions: int
    this_week_sessions: int
    total_training_minutes: int
    recent_metrics: List[MetricResponse]
    performance_trend: str


# ==================== Generic ====================
class SuccessResponse(BaseModel):
    success: bool

class ErrorResponse(BaseModel):
    detail: str
'''
        
        # Add conditional schemas
        if "openai" in self._enabled_integrations:
            schemas_code += '''

# ==================== Insights (OpenAI) ====================
class InsightRequest(BaseModel):
    insight_type: str = Field(..., pattern="^(training_advice|recovery|nutrition)$")

class InsightResponse(BaseModel):
    id: UUID
    user_id: UUID
    insight_type: str
    content: str
    context: Optional[dict]
    created_at: datetime
    class Config:
        from_attributes = True

class InsightListResponse(BaseModel):
    insights: List[InsightResponse]
'''
        
        if "stripe" in self._enabled_integrations:
            schemas_code += '''

# ==================== Billing (Stripe) ====================
class CheckoutRequest(BaseModel):
    plan: str = Field(..., pattern="^(pro|premium)$")

class CheckoutResponse(BaseModel):
    checkout_url: str

class SubscriptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    stripe_subscription_id: str
    plan: str
    status: str
    current_period_end: Optional[datetime]
    class Config:
        from_attributes = True
'''
        
        self._write_file(output_dir, "app/schemas/schemas.py", schemas_code)
        logger.info("Backend Agent: Pydantic schemas generated.")

    def _generate_api_handlers(self, output_dir: str, design: Dict[str, Any]):
        """Generates FastAPI endpoint handlers for core functionality."""
        
        # Sessions endpoint
        sessions_code = '''"""Training Sessions API endpoints."""
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
'''
        self._write_file(output_dir, "app/api/v1/endpoints/sessions.py", sessions_code)

        # Metrics endpoint
        metrics_code = '''"""Performance Metrics API endpoints."""
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
'''
        self._write_file(output_dir, "app/api/v1/endpoints/metrics.py", metrics_code)

        # Users endpoint
        users_code = '''"""User Profile API endpoints."""
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
'''
        self._write_file(output_dir, "app/api/v1/endpoints/users.py", users_code)

        # Dashboard endpoint
        dashboard_code = '''"""Dashboard Statistics API endpoints."""
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
'''
        self._write_file(output_dir, "app/api/v1/endpoints/dashboard.py", dashboard_code)

        # API router - dynamically include endpoints
        router_imports = ["from fastapi import APIRouter", "", "from app.api.v1.endpoints import sessions, metrics, users, dashboard, auth"]
        router_includes = [
            'api_router.include_router(auth.router, prefix="/auth", tags=["auth"])',
            'api_router.include_router(users.router, prefix="/users", tags=["users"])',
            'api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])',
            'api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])',
            'api_router.include_router(dashboard.router, prefix="/stats/dashboard", tags=["dashboard"])',
        ]
        
        if "openai" in self._enabled_integrations:
            router_imports[2] += ", insights"
            router_includes.append('api_router.include_router(insights.router, prefix="/insights", tags=["insights"])')
        
        if "stripe" in self._enabled_integrations:
            router_imports[2] += ", billing"
            router_includes.append('api_router.include_router(billing.router, prefix="/billing", tags=["billing"])')

        router_code = "\n".join(router_imports) + "\n\napi_router = APIRouter()\n\n" + "\n".join(router_includes) + "\n"
        self._write_file(output_dir, "app/api/v1/router.py", router_code)
        
        logger.info("Backend Agent: API handlers generated.")

    def _generate_auth(self, output_dir: str, design: Dict[str, Any]):
        """Generates authentication with Supabase Auth."""
        auth_code = '''"""Authentication endpoints using Supabase Auth."""
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
'''
        self._write_file(output_dir, "app/api/v1/endpoints/auth.py", auth_code)

        # Dependencies
        deps_code = '''"""Dependency injection for FastAPI."""
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
'''
        self._write_file(output_dir, "app/core/deps.py", deps_code)
        logger.info("Backend Agent: Authentication generated.")

    def _generate_stripe_integration(self, output_dir: str, design: Dict[str, Any]):
        """Generates Stripe payment integration (only if enabled)."""
        billing_code = '''"""Stripe Billing API endpoints."""
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
'''
        self._write_file(output_dir, "app/api/v1/endpoints/billing.py", billing_code)
        logger.info("Backend Agent: Stripe integration generated.")

    def _generate_openai_integration(self, output_dir: str, design: Dict[str, Any]):
        """Generates OpenAI AI insights integration (only if enabled)."""
        insights_code = '''"""AI Insights API endpoints using OpenAI."""
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
    session_summary = "\\n".join([f"- {s.session_date}: {s.sport_type}, {s.duration_minutes}min" for s in sessions]) or "No sessions"
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert sports performance coach."},
                {"role": "user", "content": f"Recent training:\\n{session_summary}\\n\\n{PROMPTS.get(request.insight_type, PROMPTS['training_advice'])}"}
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
'''
        self._write_file(output_dir, "app/api/v1/endpoints/insights.py", insights_code)
        logger.info("Backend Agent: OpenAI integration generated.")

    def _generate_main_app(self, output_dir: str, design: Dict[str, Any]):
        """Generates the main FastAPI application."""
        project_name = self._get_project_name(design)
        
        main_code = f'''"""Main FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {{settings.PROJECT_NAME}}...")
    yield
    print("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="{self._get_description(design)}",
    version="1.0.0",
    openapi_url=f"{{settings.API_V1_PREFIX}}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "version": "1.0.0"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        self._write_file(output_dir, "app/main.py", main_code)
        
        session_code = '''"""Database session configuration."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
'''
        self._write_file(output_dir, "app/db/session.py", session_code)
        logger.info("Backend Agent: Main application generated.")

    def _generate_config(self, output_dir: str, design: Dict[str, Any]):
        """Generates application configuration."""
        config_lines = [
            '"""Application configuration using Pydantic Settings."""',
            'from typing import List',
            'from pydantic_settings import BaseSettings',
            '',
            'class Settings(BaseSettings):',
            f'    PROJECT_NAME: str = "{self._get_project_name(design)} API"',
            '    API_V1_PREFIX: str = "/api/v1"',
            '    ENVIRONMENT: str = "development"',
            '    SECRET_KEY: str = "change-me-in-production"',
            '    ',
            '    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]',
            '    FRONTEND_URL: str = "http://localhost:3000"',
            '    ',
            '    DATABASE_URL: str = "postgresql://localhost/db"',
            '    SUPABASE_URL: str = ""',
            '    SUPABASE_ANON_KEY: str = ""',
            '    SUPABASE_SERVICE_ROLE_KEY: str = ""',
        ]
        
        if "stripe" in self._enabled_integrations:
            config_lines.extend([
                '    ',
                '    STRIPE_SECRET_KEY: str = ""',
                '    STRIPE_WEBHOOK_SECRET: str = ""',
                '    STRIPE_PRICE_PRO: str = ""',
                '    STRIPE_PRICE_PREMIUM: str = ""',
            ])
        
        if "openai" in self._enabled_integrations:
            config_lines.extend([
                '    ',
                '    OPENAI_API_KEY: str = ""',
            ])
        
        config_lines.extend([
            '    ',
            '    class Config:',
            '        env_file = ".env"',
            '        case_sensitive = True',
            '',
            'settings = Settings()',
        ])
        
        self._write_file(output_dir, "app/core/config.py", "\n".join(config_lines))
        logger.info("Backend Agent: Configuration generated.")

    def _generate_tests(self, output_dir: str, design: Dict[str, Any]):
        """Generates pytest tests."""
        conftest_code = '''"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock

from app.main import app
from app.core.deps import get_db, get_current_user, get_supabase
from app.models.models import Base, Users

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_user(db):
    from uuid import uuid4
    user = Users(id=uuid4(), email="test@example.com", full_name="Test User", sport="running", subscription_tier="pro")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def client(test_user):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_supabase] = lambda: MagicMock()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
'''
        self._write_file(output_dir, "tests/conftest.py", conftest_code)

        session_tests = '''"""Tests for training sessions API."""
from datetime import date

def test_create_session(client):
    response = client.post("/api/v1/sessions", json={
        "session_date": str(date.today()), "sport_type": "running", "duration_minutes": 45
    })
    assert response.status_code == 201
    assert response.json()["sport_type"] == "running"

def test_list_sessions(client):
    client.post("/api/v1/sessions", json={"session_date": str(date.today()), "sport_type": "cycling", "duration_minutes": 60})
    response = client.get("/api/v1/sessions")
    assert response.status_code == 200
    assert "sessions" in response.json()
'''
        self._write_file(output_dir, "tests/api/test_sessions.py", session_tests)

        health_test = '''"""Basic API tests."""
from fastapi.testclient import TestClient
from app.main import app

def test_health_check():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
'''
        self._write_file(output_dir, "tests/api/test_health.py", health_test)
        logger.info("Backend Agent: Tests generated.")

    def _write_file(self, directory: str, filename: str, content: str):
        """Write content to a file."""
        filepath = os.path.join(directory, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        logger.info(f"Backend Agent: Wrote {filename}")
