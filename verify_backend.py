"""
Verification script for Backend Agent.
Tests the agent's ability to generate a complete FastAPI backend from system_design.json.
"""
import sys
import os
import shutil
from unittest.mock import MagicMock

# Mock DBClient before importing agent
import core.base_agent
core.base_agent.DBClient = MagicMock()

from agents.backend_agent import BackendAgent
from infrastructure.event_bus import EventBus


def test_backend_generation():
    """Test that the backend agent generates all expected files."""
    industry = "athletes"
    output_dir = f"output/{industry}/backend"
    
    # Cleanup previous run
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    print("=" * 60)
    print("Backend Agent Verification")
    print("=" * 60)
    print()
    
    print("1. Initializing Backend Agent...")
    bus = EventBus()
    agent = BackendAgent("backend", bus)
    print(f"   ✓ Agent role: {agent.role}")
    print()

    print(f"2. Generating backend code for '{industry}'...")
    agent.generate_code_from_designs(industry)
    print()

    # Core files that should always be generated
    print("3. Verifying core generated files...")
    core_files = [
        "requirements.txt",
        "pyproject.toml",
        ".env.example",
        ".gitignore",
        "migrations/001_initial_schema.sql",
        "app/__init__.py",
        "app/main.py",
        "app/core/__init__.py",
        "app/core/config.py",
        "app/core/deps.py",
        "app/db/__init__.py",
        "app/db/session.py",
        "app/models/__init__.py",
        "app/models/models.py",
        "app/schemas/__init__.py",
        "app/schemas/schemas.py",
        "app/api/__init__.py",
        "app/api/v1/__init__.py",
        "app/api/v1/router.py",
        "app/api/v1/endpoints/__init__.py",
        "app/api/v1/endpoints/auth.py",
        "app/api/v1/endpoints/users.py",
        "app/api/v1/endpoints/sessions.py",
        "app/api/v1/endpoints/metrics.py",
        "app/api/v1/endpoints/dashboard.py",
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/api/test_health.py",
        "tests/api/test_sessions.py",
    ]

    missing = []
    for f in core_files:
        path = os.path.join(output_dir, f)
        if not os.path.exists(path):
            missing.append(f)
    
    print(f"   ✓ Core files found: {len(core_files) - len(missing)}/{len(core_files)}")
    
    if missing:
        print(f"\n   ✗ Missing core files:")
        for m in missing:
            print(f"      - {m}")
        print("\nFAILED: Some core files are missing.")
        sys.exit(1)
    
    print()
    
    # Check conditional integration files based on what's enabled
    print("4. Verifying conditional integrations...")
    enabled_integrations = agent._enabled_integrations
    print(f"   Enabled integrations: {enabled_integrations}")
    
    if "stripe" in enabled_integrations:
        stripe_file = os.path.join(output_dir, "app/api/v1/endpoints/billing.py")
        if not os.path.exists(stripe_file):
            print("   ✗ Stripe enabled but billing.py not found")
            sys.exit(1)
        print("   ✓ Stripe integration: billing.py exists")
    else:
        print("   - Stripe: skipped (not in design)")
    
    if "openai" in enabled_integrations:
        openai_file = os.path.join(output_dir, "app/api/v1/endpoints/insights.py")
        if not os.path.exists(openai_file):
            print("   ✗ OpenAI enabled but insights.py not found")
            sys.exit(1)
        print("   ✓ OpenAI integration: insights.py exists")
    else:
        print("   - OpenAI: skipped (not in design)")
    
    print()
    
    # Verify key file contents
    print("5. Verifying file contents...")
    
    # Check main.py
    with open(os.path.join(output_dir, "app/main.py"), 'r') as f:
        main_content = f.read()
        if "FastAPI" not in main_content or "api_router" not in main_content:
            print("   ✗ main.py content verification failed")
            sys.exit(1)
    print("   ✓ app/main.py - FastAPI app configured correctly")
    
    # Check migrations
    with open(os.path.join(output_dir, "migrations/001_initial_schema.sql"), 'r') as f:
        migration_content = f.read()
        if "CREATE TABLE" not in migration_content or "users" not in migration_content:
            print("   ✗ migrations verification failed")
            sys.exit(1)
        if "ROW LEVEL SECURITY" not in migration_content:
            print("   ✗ RLS policies not found in migrations")
            sys.exit(1)
    print("   ✓ migrations/001_initial_schema.sql - DB schema with RLS")
    
    # Check models (fixed: check for class definitions, not "SQLAlchemy" literal)
    with open(os.path.join(output_dir, "app/models/models.py"), 'r') as f:
        models_content = f.read()
        if "class Users" not in models_content or "DeclarativeBase" not in models_content:
            print("   ✗ models verification failed")
            sys.exit(1)
    print("   ✓ app/models/models.py - SQLAlchemy models defined")
    
    # Check schemas
    with open(os.path.join(output_dir, "app/schemas/schemas.py"), 'r') as f:
        schemas_content = f.read()
        if "BaseModel" not in schemas_content:
            print("   ✗ schemas verification failed")
            sys.exit(1)
    print("   ✓ app/schemas/schemas.py - Pydantic validation schemas")
    
    # Check conditional integration content
    if "stripe" in enabled_integrations:
        with open(os.path.join(output_dir, "app/api/v1/endpoints/billing.py"), 'r') as f:
            billing_content = f.read()
            if "stripe" not in billing_content or "checkout" not in billing_content.lower():
                print("   ✗ Stripe integration verification failed")
                sys.exit(1)
        print("   ✓ app/api/v1/endpoints/billing.py - Stripe integration")
    
    if "openai" in enabled_integrations:
        with open(os.path.join(output_dir, "app/api/v1/endpoints/insights.py"), 'r') as f:
            insights_content = f.read()
            if "openai" not in insights_content or "gpt-4" not in insights_content:
                print("   ✗ OpenAI integration verification failed")
                sys.exit(1)
        print("   ✓ app/api/v1/endpoints/insights.py - OpenAI GPT-4 integration")
    
    print()
    print("=" * 60)
    print("SUCCESS! Backend Agent verification passed.")
    print("=" * 60)
    print()
    print(f"Generated files in: {os.path.abspath(output_dir)}")
    print()
    print("Key features implemented:")
    print("  • FastAPI application with health check")
    print("  • Supabase PostgreSQL migrations with RLS")
    print("  • SQLAlchemy models for core entities")
    print("  • Pydantic schemas for request/response validation")
    print("  • Auth endpoints with Supabase Auth")
    print("  • CRUD endpoints for sessions and metrics")
    print("  • Dashboard statistics API")
    if "stripe" in enabled_integrations:
        print("  • Stripe billing integration (checkout, webhooks)")
    if "openai" in enabled_integrations:
        print("  • OpenAI GPT-4 AI insights")
    print("  • Pytest test fixtures and tests")


if __name__ == "__main__":
    test_backend_generation()
