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
    # --- 1. RUN DATABASE MIGRATIONS AS A SUBPROCESS ---
    print("--- Running database migrations via subprocess ---")
    
    # This command runs 'alembic upgrade head' from the shell.
    # The 'cwd' argument tells it to run the command from the '/app' directory,
    # which is the container's working directory and where alembic.ini is.
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
        cwd="/app"  # This is the crucial part
    )
    
    # Check if the migration failed and print the error
    if result.returncode != 0:
        print("🔴 MIGRATION FAILED:")
        print("--- STDOUT ---")
        print(result.stdout)
        print("--- STDERR ---")
        print(result.stderr)
        # Stop the application from starting if migrations fail
        raise Exception("Could not apply database migrations.")
    
    print("✅ Database migrations complete.")
    print(result.stdout)

    # --- 2. CREATE ADMIN USER (IF NOT EXISTS) ---
    print("--- Checking for admin user ---")
    async with async_session() as session:
        async with session.begin():
            stmt = text("SELECT username FROM users WHERE username = :username")
            result = await session.execute(stmt, {"username": "admin"})
            existing_user = result.fetchone()

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
                print("✅ Admin user created successfully!")
            else:
                print("✅ Admin user already exists.")
# -------------------------
# Startup event
# -------------------------
#@app.on_event("startup")
#async def on_startup():
    # Initialize tables
 #   await init_models()

