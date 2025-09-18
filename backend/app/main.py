from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text

# --- These are the only imports needed for startup ---
from .db import engine, Base, async_session
from .models import User
from .auth import get_password_hash
from .config import settings
from .api import v1

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI(title="Coimbatore Caterers CRM", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(v1.router, prefix="/api/v1")


# -------------------------
# Startup event - The Final, Simplest Version
# -------------------------
@app.on_event("startup")
async def on_startup():
    # --- STEP 1: CREATE ALL DATABASE TABLES ---
    # This command is a direct, built-in SQLAlchemy function.
    # It looks at your models (User, Lead, etc.) and creates the
    # tables if they don't already exist. It is safe to run every time.
    print("--- Creating database tables (if they don't exist)... ---")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("--- Tables are ready. ---")

    # --- STEP 2: CREATE THE ADMIN USER (IF IT DOESN'T EXIST) ---
    # This is your trusted logic to create the user.
    print("--- Checking for admin user... ---")
    async with async_session() as session:
        async with session.begin():
            # Check if the user already exists
            stmt = select(User).where(User.username == "admin")
            result = await session.execute(stmt)
            existing_user = result.scalars().first()

            if not existing_user:
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
            else:
                print("--- Admin user already exists. No action taken. ---")
