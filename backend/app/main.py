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
    print("--- Initializing database on startup ---")
    
    # We will perform all setup in a single connection and transaction
    # to guarantee the order of operations.
    async with engine.begin() as conn:
        
        # --- STEP 1: FORCE CREATE ALL TABLES ---
        # This command is a direct, built-in SQLAlchemy function.
        # It inspects your models (User, Lead, etc.) and issues the
        # CREATE TABLE IF NOT EXISTS commands.
        print("Creating database tables (if they don't exist)...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables are ready.")
        
        # --- STEP 2: CREATE THE ADMIN USER (IF IT DOESN'T EXIST) ---
        # This command runs second, inside the SAME transaction.
        print("Checking for admin user...")
        
        # We use the connection to check if the user exists.
        # This is guaranteed to run after the tables are created.
        result = await conn.execute(
            select(User).where(User.username == "admin")
        )
        existing_user = result.scalars().first()

        if not existing_user:
            print("Admin user not found, creating one...")
            hashed_password = get_password_hash("admin123")
            
            # We use the connection to insert the new user
            await conn.execute(
                User.__table__.insert().values(
                    username="admin",
                    password_hash=hashed_password,
                    full_name="Admin User",
                    role="Admin"
                )
            )
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")
            
    print("--- Database initialization complete. ---")