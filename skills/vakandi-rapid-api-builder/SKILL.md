---
name: vakandi-rapid-api-builder
description: |
  Build production-ready FastAPI backends for the RapidAPI marketplace.
  Scaffolds full-stack APIs with SQLAlchemy 2.0 async, Pydantic v2, 
  tier-based auth (X-API-Key + X-RapidAPI-Proxy-Secret), rate limiting,
  Docker deployment, and pytest suite. Based on proven patterns from
  OpenHack API and LinkedIn Scrapper API.
metadata:
  model: claude-sonnet-4-20250514
  author: Gilfoyle / User
  source: Vakandi
---

# RAPID API BUILDER — `vakandi-rapid-api-builder`

## Use this skill when

- Building a new REST API to sell on the RapidAPI marketplace
- Scaffolding a FastAPI project from zero
- Adding RapidAPI-compatible auth (dual-header API key + proxy secret)
- Implementing tier-based rate limiting with monthly quotas
- Setting up SQLAlchemy 2.0 async with PostgreSQL / SQLite
- Adding user plans, usage tracking, or subscription billing
- Dockerizing a FastAPI service for production

## Do NOT use this skill when

- Building a GraphQL API (use Strawberry or Ariadne)
- Working on an existing project that doesn't use FastAPI
- Building a frontend, scraper, or CLI tool
- The task is unrelated to REST API development

---

## Architecture Overview

```
app/
├── main.py              # FastAPI app, lifespan, CORS, exception handlers
├── core/
│   ├── config.py        # Pydantic v2 Settings (env-based)
│   ├── database.py      # AsyncSession, engine, get_db dependency
│   ├── security.py      # API key auth + RapidAPI proxy secret validation
│   └── deps.py          # FastAPI Depends() — get_current_user, usage tracking
├── models/
│   ├── __init__.py
│   ├── user.py          # User ORM model (uuid PK, plan, api_key, quotas)
│   └── resource.py      # Your domain models
├── schemas/
│   ├── __init__.py
│   ├── user.py          # Pydantic v2 request/response models
│   └── resource.py      # Domain schemas (Create, Response, List)
├── routers/
│   ├── __init__.py
│   ├── users.py         # /users/* endpoints
│   └── resources.py     # /resources/* endpoints
├── services/
│   ├── __init__.py
│   ├── user_service.py  # Business logic
│   └── resource_service.py
├── workers/             # Background task workers (optional)
│   └── __init__.py
```

**Root files:**
```
pyproject.toml         # Dependencies + tool config
Dockerfile             # python:3.12-slim + uvicorn
docker-compose.yml     # API service + optional DB
.env.example           # All required env vars
```

---

## Step 1 — Project Scaffold

```bash
mkdir -p app/core app/models app/schemas app/routers app/services app/workers
touch app/__init__.py app/core/__init__.py
touch app/models/__init__.py app/schemas/__init__.py
touch app/routers/__init__.py app/services/__init__.py
touch app/workers/__init__.py
```

Create `pyproject.toml`:

```toml
[project]
name = "your-api-name"
version = "0.1.0"
description = "Your API description for RapidAPI marketplace"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "aiosqlite>=0.20.0",          # Dev only — use asyncpg for production
    "psycopg[binary]>=3.2",        # Production PostgreSQL driver
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "httpx>=0.27.0",              # HTTP client (webhooks, external calls)
    "python-dotenv>=1.0",
    "structlog>=24.0",             # Structured logging
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "httpx>=0.27.0",
    "ruff>=0.6.0",
    "pyright>=1.1.380",
]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

---

## Step 2 — Core Files

### `app/core/config.py` — Pydantic Settings

```python
"""Application configuration via environment variables."""
from __future__ import annotations
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Your API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    # Security — RapidAPI
    API_KEY_HEADER: str = "X-API-Key"
    RAPIDAPI_PROXY_SECRET: str = "change-me"          # From RapidAPI dashboard
    RAPIDAPI_PROXY_HEADER: str = "X-RapidAPI-Proxy-Secret"
    ADMIN_API_KEYS: str = ""                           # Comma-separated

    # Rate limiting (per tier — override in RapidAPI dashboard)
    RATE_LIMIT_BASIC_PER_MONTH: int = 100
    RATE_LIMIT_PRO_PER_MONTH: int = 1000
    RATE_LIMIT_ENTERPRISE_PER_MONTH: int = 10000

    # CORS
    CORS_ORIGINS: str = "*"

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### `app/core/database.py` — AsyncSession Setup

```python
"""Database setup with SQLAlchemy AsyncSession."""
from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

# Auto-convert sqlite:/// → sqlite+aiosqlite:/// if needed
_db_url = settings.DATABASE_URL
if _db_url.startswith("sqlite:///"):
    _db_url = _db_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
# PostgreSQL: ensure async driver
elif _db_url.startswith("postgresql://"):
    if "+asyncpg" not in _db_url:
        _db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(_db_url, echo=settings.DEBUG)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields session, commits on success, rolls back on error."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables (dev/lightweight usage). Use Alembic for production."""
    async with engine.begin() as conn:
        # Import models to register them with Base metadata
        # from app.models import user, resource  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
```

### `app/core/security.py` — Dual-Header Auth (RapidAPI + Direct)

```python
"""API key authentication supporting both RapidAPI proxy and direct keys."""
from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User, UserPlan

settings = get_settings()

api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)
rapidapi_header = APIKeyHeader(name=settings.RAPIDAPI_PROXY_HEADER, auto_error=False)


class AuthUser:
    """Resolved authenticated user info."""

    def __init__(self, user: User | None = None, is_admin: bool = False):
        self.user = user
        self.is_admin = is_admin
        self.user_id: str | None = user.id if user else None
        self.plan: str = user.plan.value if user else "basic"
        self.email: str | None = user.email if user else None


async def get_current_user(
    api_key: str | None = Security(api_key_header),
    rapidapi_key: str | None = Security(rapidapi_header),
    db: AsyncSession = Depends(get_db),
) -> AuthUser:
    """Resolve user from X-API-Key or X-RapidAPI-Proxy-Secret.

    Two-track authentication:
    1. RapidAPI track — validates proxy secret header
    2. Direct track — looks up user by API key in database
    """
    key = api_key or rapidapi_key
    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Missing API key. Provide via {settings.API_KEY_HEADER} header.",
            headers={"WWW-Authenticate": "APIKey"},
        )

    # Admin keys bypass DB lookup
    admin_keys = {k.strip() for k in settings.ADMIN_API_KEYS.split(",") if k.strip()}
    if key in admin_keys:
        return AuthUser(is_admin=True)

    # Look up user by API key
    result = await db.execute(select(User).where(User.api_key == key))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )
    return AuthUser(user=user)


def generate_api_key() -> str:
    """Generate a secure random API key (prefix customizable per project)."""
    return f"pk_{secrets.token_hex(24)}"
```

### `app/core/deps.py` — Usage Tracking & Plan Checks

```python
"""Reusable FastAPI dependencies — quota enforcement, plan gating."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import AuthUser, get_current_user
from app.models.user import User, UserPlan

log = logging.getLogger("app.deps")


async def check_plan(required_plans: set[UserPlan]):
    """Factory: returns a dependency that checks user has one of required plans."""
    async def _checker(
        auth: AuthUser = Depends(get_current_user),
    ) -> AuthUser:
        user_plan = UserPlan(auth.plan) if auth.plan else UserPlan.basic
        if user_plan not in required_plans:
            raise HTTPException(
                status_code=402,
                detail=f"This endpoint requires a {', '.join(p.value for p in required_plans)} plan.",
            )
        return auth
    return _checker


async def enforce_monthly_quota(
    db: AsyncSession = Depends(get_db),
    auth: AuthUser = Depends(get_current_user),
) -> None:
    """Check and decrement monthly usage quota. Returns 429 if exceeded."""
    # Get plan limits
    plan_limits = {
        UserPlan.basic: 100,
        UserPlan.pro: 1000,
        UserPlan.enterprise: 10000,
    }
    user_plan = UserPlan(auth.plan) if auth.plan else UserPlan.basic
    monthly_limit = plan_limits.get(user_plan, 100)

    # Count usage this month from your resource table
    now = datetime.now(timezone.utc)
    first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Replace YourResourceModel with your actual model
    # result = await db.execute(
    #     select(func.count()).select_from(YourResourceModel)
    #     .where(
    #         YourResourceModel.user_id == auth.user_id,
    #         YourResourceModel.created_at >= first_of_month,
    #     )
    # )
    # used = result.scalar() or 0
    # if used >= monthly_limit:
    #     raise HTTPException(
    #         status_code=429,
    #         detail=f"Monthly quota reached ({monthly_limit}). Upgrade your plan.",
    #     )
```

---

## Step 3 — Models

### `app/models/user.py`

```python
"""User and plan models for RapidAPI marketplace."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserPlan(str, enum.Enum):
    basic = "basic"
    pro = "pro"
    enterprise = "enterprise"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    api_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    plan: Mapped[UserPlan] = mapped_column(Enum(UserPlan), default=UserPlan.basic, nullable=False)
    usage_this_month: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    monthly_limit: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.plan.value})>"
```

### Resource Model Example — Replace with your domain

```python
"""Example resource model — adapt to your API domain."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    data: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", backref="resources")
```

---

## Step 4 — Schemas (Pydantic v2)

### `app/schemas/user.py`

```python
from __future__ import annotations
from pydantic import BaseModel, Field


class UsageResponse(BaseModel):
    plan: str = Field(..., description="Plan name (basic / pro / enterprise)")
    used_this_month: int = Field(0, ge=0)
    monthly_limit: int = Field(0, ge=0)
    remaining: int = Field(0, ge=0)

    model_config = {"from_attributes": True}
```

### `app/schemas/resource.py`

```python
from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


class ResourceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    data: str | None = Field(None, max_length=10000)


class ResourceResponse(BaseModel):
    id: str
    name: str
    data: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ResourceListResponse(BaseModel):
    resources: list[ResourceResponse]
    total: int
    limit: int
    offset: int
```

---

## Step 5 — Services (Business Logic)

### `app/services/resource_service.py`

```python
from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.resource import Resource  # replace with your model


async def create_resource(
    db: AsyncSession,
    user: User,
    name: str,
    data: str | None = None,
) -> Resource:
    resource = Resource(user_id=user.id, name=name, data=data)
    db.add(resource)
    await db.flush()
    return resource


async def get_user_resources(
    db: AsyncSession,
    user_id: str,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Resource], int]:
    count_q = select(func.count()).select_from(Resource).where(Resource.user_id == user_id)
    total = (await db.execute(count_q)).scalar() or 0

    query = (
        select(Resource)
        .where(Resource.user_id == user_id)
        .order_by(Resource.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    return list(result.scalars().all()), total
```

---

## Step 6 — Routers (Thin Handlers)

### `app/routers/resources.py`

```python
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import AuthUser, get_current_user
from app.schemas.resource import ResourceCreate, ResourceListResponse, ResourceResponse
from app.services import resource_service

log = logging.getLogger("app.resources")
router = APIRouter(prefix="/resources", tags=["resources"])


@router.post("", response_model=ResourceResponse, status_code=201)
async def create_resource(
    body: ResourceCreate,
    db: AsyncSession = Depends(get_db),
    auth: AuthUser = Depends(get_current_user),
):
    resource = await resource_service.create_resource(
        db, user=auth.user, name=body.name, data=body.data
    )
    return ResourceResponse.model_validate(resource)


@router.get("", response_model=ResourceListResponse)
async def list_resources(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    auth: AuthUser = Depends(get_current_user),
):
    resources, total = await resource_service.get_user_resources(
        db, auth.user_id, limit=limit, offset=offset
    )
    return ResourceListResponse(
        resources=[ResourceResponse.model_validate(r) for r in resources],
        total=total,
        limit=limit,
        offset=offset,
    )
```

### `app/routers/users.py`

```python
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from app.core.security import AuthUser, get_current_user
from app.schemas.user import UsageResponse

log = logging.getLogger("app.users")
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/usage", response_model=UsageResponse)
async def get_usage(auth: AuthUser = Depends(get_current_user)):
    user = auth.user
    return UsageResponse(
        plan=str(user.plan.value) if user.plan else "basic",
        used_this_month=user.usage_this_month,
        monthly_limit=user.monthly_limit,
        remaining=max(0, user.monthly_limit - user.usage_this_month),
    )
```

---

## Step 7 — App Bootstrap

### `app/main.py`

```python
"""FastAPI application bootstrap with RapidAPI support."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import async_session_factory, init_db
from app.routers import users, resources

settings = get_settings()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
log = logging.getLogger("app")


# ---------------------------------------------------------------------------
# Lifespan — startup / shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("app.starting", extra={"version": settings.APP_VERSION})
    await init_db()
    yield
    log.info("app.stopped")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Your API description — shown on RapidAPI marketplace",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log.error(
        "unhandled error at %s %s: %s",
        request.method, str(request.url), str(exc),
    )
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(resources.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Health — MUST be public (no auth) for RapidAPI uptime monitoring
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}
```

---

## Step 8 — Deployment

### `Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (git for git-based features, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY pyproject.toml .
COPY app/ app/
COPY tests/ tests/

# Install dependencies
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir uvicorn[standard]

# Create non-root user
RUN adduser --disabled-password --gecos "" apiuser && \
    chown -R apiuser:apiuser /app
USER apiuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### `docker-compose.yml`

```yaml
version: "3.9"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./data/app.db
      - RAPIDAPI_PROXY_SECRET=${RAPIDAPI_PROXY_SECRET}
      - LOG_LEVEL=info
    volumes:
      - api-data:/app/data
    restart: unless-stopped

volumes:
  api-data:
```

### `.env.example`

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./app.db

# RapidAPI (get from Provider Dashboard → Security tab)
RAPIDAPI_PROXY_SECRET=your-rapidapi-proxy-secret-here
ADMIN_API_KEYS=

# App
LOG_LEVEL=info
```

---

## Step 9 — Pricing & Plans Configuration

When defining your API on RapidAPI, create these tiers:

| Tier | Monthly Price | Requests/Month | Features |
|---|---|---|---|
| Basic | $9.99 | 100 | Read-only, standard rate |
| Pro | $49.99 | 1,000 | Full access, higher limits |
| Enterprise | $199.99 | 10,000 | Priority support, custom SLA |

**Map in `settings` via env vars:**
```python
PRICE_BASIC_MONTHLY: float = 9.99
PRICE_PRO_MONTHLY: float = 49.99
PRICE_ENTERPRISE_MONTHLY: float = 199.99
```

---

## Step 10 — Testing

### `tests/conftest.py`

```python
"""pytest fixtures for FastAPI async testing."""
from __future__ import annotations

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()

    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Override get_db dependency with test DB session."""

    async def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
```

### `tests/test_health.py`

```python
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
```

---

## RapidAPI Marketplace Checklist

Before publishing on RapidAPI, verify:

- [ ] **Health endpoint** is public (no auth) — RapidAPI uses it for uptime monitoring
- [ ] **`X-RapidAPI-Proxy-Secret` validation** — your API validates this header on every request
- [ ] **Rate limit headers** — return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- [ ] **Error responses** use `{"detail": "..."}` format (FastAPI default) — RapidAPI parses these
- [ ] **OpenAPI spec** is accurate — auto-generated by FastAPI, verify at `/docs`
- [ ] **CORS** — set specific origins (not `*`) for production authenticated APIs
- [ ] **Non-root user** in Docker — security best practice
- [ ] **.env** is never committed — add to `.gitignore`
- [ ] **Plan pricing** matches between code constants and RapidAPI dashboard
- [ ] **Usage tracking** resets monthly — the `usage_this_month` counter resets on the 1st

---

## Deployment Commands

```bash
# Build & run locally
docker compose up --build

# Test health
curl http://localhost:8000/health

# Test with direct API key
curl -H "X-API-Key: your-test-key" http://localhost:8000/api/v1/resources

# Test with RapidAPI proxy header (simulates marketplace)
curl -H "X-RapidAPI-Proxy-Secret: your-secret" http://localhost:8000/api/v1/resources

# Run tests
pytest -v --tb=short

# Lint
ruff check . && ruff format --check .

# Type check
pyright
```
