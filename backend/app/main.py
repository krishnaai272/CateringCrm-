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
from sqlalchemy import text

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
    
    # Get the directory where main.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    alembic_ini_path = os.path.join(current_dir, "alembic.ini")
    
    alembic_cfg = Config(alembic_ini_path)
    command.upgrade(alembic_cfg, "head")
    print("Database migrations complete.")

    # --- 2. CREATE ADMIN USER (IF NOT EXISTS) ---
    print("Checking for admin user...")
    async with async_session() as session:
        async with session.begin():
            # Use a simple text query to be robust
            stmt = text("SELECT username FROM users WHERE username = :username")
            result = await session.execute(stmt, {"username": "admin"})
            existing_user = result.fetchone()

            if not existing_user:
                print("Admin user not found, creating one...")
                hashed_password = get_password_hash("admin123")
                insert_stmt = text(
                    "INSERT INTO users (username, password_hash, full_name, role, created_at) "
                    "VALUES (:username, :password_hash, :full_name, :role, NOW())"
                )
                await session.execute(
                    insert_stmt,
                    {
                        "username": "admin",
                        "password_hash": hashed_password,
                        "full_name": "Admin User",
                        "role": "Admin",
                    },
                )
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

