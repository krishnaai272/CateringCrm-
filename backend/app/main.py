from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
import asyncio
from alembic.config import Config
from alembic import command
import subprocess
from sqlalchemy import text # Use text for robustness

from .config import settings
from .db import engine, Base
from .api import v1  # Import your API router
from .models import User
from .auth import get_password_hash
from .db import async_session
from sqlalchemy import select
import os
from sqlalchemy import text
from sqlalchemy import select
from .db import engine, Base, async_session
from .models import User
from .auth import get_password_hash

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
    # --- STEP 1: CREATE ALL DATABASE TABLES ---
    # This command looks at all your models (User, Lead, etc.) and creates the
    # tables if they don't already exist. It is safe to run every time.
    print("--- Creating database tables (if they don't exist)... ---")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("--- Tables are ready. ---")

    # --- STEP 2: CREATE THE ADMIN USER (IF IT DOESN'T EXIST) ---
    # This is the logic from your create_user.py script, now running automatically.
    print("--- Checking for admin user... ---")
    async with async_session() as session:
        async with session.begin():
            # Check if the user already exists
            stmt = select(User).where(User.username == "admin")
            result = await session.execute(stmt)
            existing_user = result.scalars().first()

            if existing_user:
                print("--- Admin user already exists. No action taken. ---")
                return

            # If not, create the new user
            print("--- Admin user not found, creating one... ---")
            hashed_password = get_password_hash("admin123")
            new_admin_user = User(
                username="admin",
                password_hash=hashed_password,
                full_name="Admin User",
                role="Admin",
            )
            session.add(new_admin_user)
            await session.commit()
            print("--- Admin user created successfully! ---")

# -------------------------
# Startup event
# -------------------------
#@app.on_event("startup")
#async def on_startup():
    # Initialize tables
 #   await init_models()

