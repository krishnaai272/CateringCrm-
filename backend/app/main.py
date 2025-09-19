from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from .db import engine, Base, async_session
from .models import User
from .auth import get_password_hash
from .config import settings
from .api import v1

app = FastAPI(title="Coimbatore Caterers CRM", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1.router, prefix="/api/v1")

@app.on_event("startup")
async def on_startup():
    print("--- Initializing database on startup ---")
    async with engine.begin() as conn:
        print("--- Creating all tables (if they don't exist)... ---")
        await conn.run_sync(Base.metadata.create_all)
        print("--- Tables are ready. ---")
        
        print("--- Checking for admin user... ---")
        result = await conn.execute(select(User).where(User.username == "admin"))
        existing_user = result.scalars().first()

        if not existing_user:
            print("--- Admin user not found, creating one... ---")
            hashed_password = get_password_hash("admin123")
            await conn.execute(
                User.__table__.insert().values(
                    username="admin", password_hash=hashed_password, full_name="Admin User", role="Admin"
                )
            )
            print("--- Admin user created successfully! ---")
        else:
            print("--- Admin user already exists. ---")
            
    print("--- Database initialization complete. ---")