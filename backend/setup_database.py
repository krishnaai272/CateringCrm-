import asyncio
import os
import sys
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine
from passlib.context import CryptContext

# This allows the script to find your 'app' module
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.models import Base, User
# --- THIS IS THE FIX ---
# We import 'async_session', which is the correct name from your db.py file
from app.db import async_session
# --- END FIX ---

# This script gets the database URL from the command line
LIVE_DATABASE_URL = os.environ.get("LIVE_DATABASE_URL")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)

async def main():
    if not LIVE_DATABASE_URL:
        print("🔴 ERROR: LIVE_DATABASE_URL environment variable not set.")
        return

    print("--- Connecting to LIVE database... ---")
    engine = create_async_engine(LIVE_DATABASE_URL)
    
    async with engine.begin() as conn:
        print("--- Creating all tables (if they don't exist)... ---")
        await conn.run_sync(Base.metadata.create_all)
    print("--- Tables are ready. ---")
    
    # --- THIS IS THE OTHER PART OF THE FIX ---
    # We re-bind the imported async_session to use the engine we just created for this script
    async_session.configure(bind=engine)
    # --- END FIX ---
    
    async with async_session() as session:
        async with session.begin():
            stmt = select(User).where(User.username == "admin")
            result = await session.execute(stmt)
            existing_user = result.scalars().first()

            if existing_user:
                print(f"✅ User 'admin' already exists.")
            else:
                print("--- Admin user 'admin' not found, creating one... ---")
                hashed_password = get_password_hash("admin123")
                new_user = User(username="admin", password_hash=hashed_password, full_name="Admin User", role="Admin")
                session.add(new_user)
                await session.commit()
                print("✅ Admin user created successfully!")

    await engine.dispose()
    print("\n✅ Database setup is complete! You can now log in.")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())