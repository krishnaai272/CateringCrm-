import asyncio
from passlib.context import CryptContext
import sys

# Add the backend directory to the Python path to find the 'app' module
sys.path.append('./backend')

from app.db import async_session
from app.models import User
from app.auth import get_password_hash

async def create_admin_user():
    print("Connecting to the database to create an admin user...")
    
    # --- Define your admin user details here ---
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"
    # -------------------------------------------

    hashed_password = get_password_hash(ADMIN_PASSWORD)

    async with async_session() as session:
        async with session.begin():
            # Check if user already exists
            result = await session.execute(
                User.__table__.select().where(User.username == ADMIN_USERNAME)
            )
            existing_user = result.fetchone()

            if existing_user:
                print(f"User '{ADMIN_USERNAME}' already exists. No action taken.")
                return

            # Create the new user
            new_user = User(
                username=ADMIN_USERNAME,
                password_hash=hashed_password,
                full_name="Admin User",
                role="Admin",
            )
            session.add(new_user)
            await session.commit()
            
            print("\n" + "="*40)
            print("  Admin user created successfully!")
            print(f"  Username: {ADMIN_USERNAME}")
            print(f"  Password: {ADMIN_PASSWORD}")
            print("="*40 + "\n")

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(create_admin_user())