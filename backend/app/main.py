from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
import asyncio
from alembic.config import Config
from alembic import command

from .config import settings
from .db import engine, Base
from .api import v1  # Import your API router
from .models import User
from .auth import get_password_hash
from .db import async_session
from sqlalchemy import select
import os

# -------------------------
# Create tables (async)
# -------------------------
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI(title="Coimbatore Caterers CRM", version="1.0.0")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limit exception handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded"}
    )

# Include API router
app.include_router(v1.router, prefix="/api/v1", tags=["Leads"])

@app.on_event("startup")
async def on_startup():
    # --- 1. RUN DATABASE MIGRATIONS ---
    print("Running database migrations on startup...")
    
    # Now that alembic.ini is in the same directory as the code, the path is simple.
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    print("Database migrations complete.")

    # --- 2. CREATE ADMIN USER (IF NOT EXISTS) ---
    print("Checking for admin user...")
    async with async_session() as session:
        async with session.begin():
            stmt = select(User).where(User.username == "admin")
            result = await session.execute(stmt)
            existing_user = result.scalars().first()

            if not existing_user:
                print("Admin user not found, creating one...")
                hashed_password = get_password_hash("admin123")
                new_admin = User(
                    username="admin",
                    password_hash=hashed_password,
                    full_name="Admin User",
                    role="Admin"
                )
                session.add(new_admin)
                await session.commit()
                print("Admin user created successfully!")
            else:
                print("Admin user already exists.")




# -------------------------
# Startup event
# -------------------------
#@app.on_event("startup")
#async def on_startup():
    # Initialize tables
 #   await init_models()

