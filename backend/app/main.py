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

    # Create all tables (if not already present)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("--- Tables are ready. ---")

    # Open a session to check/create admin user
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.username == "admin"))
            existing_user = result.scalars().first()

            if not existing_user:
                print("--- Admin user not found, creating one... ---")
                hashed_password = get_password_hash("admin123")
                new_user = User(
                    username="admin",
                    password_hash=hashed_password,
                    full_name="Admin User",
                    role="Admin"
                )
                session.add(new_user)
                print("--- Admin user created successfully! ---")
            else:
                print("--- Admin user already exists. ---")

    print("--- Database initialization complete. ---")