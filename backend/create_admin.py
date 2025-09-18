import asyncio
import os
import sys

# --- THIS IS THE FIX ---
# We will now explicitly load the .env file from the correct location.
from dotenv import load_dotenv
# Construct the path to the .env file, which is in the same directory as this script.
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)
# --- END FIX ---

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

# This adds the parent directory ('backend') to Python's search path.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.models import User, Base
from app.auth import get_password_hash
from app.config import settings

# This script will now get the database URL from the command line,
# and all other settings (SECRET_KEY, etc.) from the loaded .env file.
LIVE_DATABASE_URL = os.environ.get("LIVE_DATABASE_URL")

async def setup_database_and_create_admin():
    # ... The rest of the script is correct and does not need to change ...
    if not LIVE_DATABASE_URL:
        # ... error message ...
        return

    print(f"--- Connecting to LIVE database... ---")
    
    # We override the DATABASE_URL from the settings with the one from the command line
    settings.DATABASE_URL = LIVE_DATABASE_URL
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with engine.begin() as conn:
        print("--- Creating all tables (if they don't exist)... ---")
        await conn.run_sync(Base.metadata.create_all)
    print("--- Tables are ready. ---")
    
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"
    hashed_password = get_password_hash(ADMIN_PASSWORD)

    async with async_session() as session:
        async with session.begin():
            stmt = select(User).where(User.username == ADMIN_USERNAME)
            result = await session.execute(stmt)
            existing_user = result.fetchone()

            if existing_user:
                print(f"✅ User '{ADMIN_USERNAME}' already exists. No action taken.")
                return

            print(f"--- Admin user '{ADMIN_USERNAME}' not found, creating one... ---")
            new_user = User(username=ADMIN_USERNAME, password_hash=hashed_password, full_name="Admin User", role="Admin")
            session.add(new_user)
            await session.commit()
            
            print("\n" + "="*40)
            print("  ✅ Admin user created successfully in the LIVE database!")
            print(f"  Username: {ADMIN_USERNAME}")
            print(f"  Password: {ADMIN_PASSWORD}")
            print("="*40 + "\n")

    await engine.dispose()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(setup_database_and_create_admin())