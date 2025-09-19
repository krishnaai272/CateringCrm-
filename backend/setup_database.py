import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text # Import text for raw SQL if needed

# Assuming Base is imported from your models.
# Adjust this import path as necessary based on your project structure.
from app.models import Base 

async def main():
    db_url = os.environ.get("LIVE_DATABASE_URL")
    if not db_url:
        print("LIVE_DATABASE_URL environment variable not set.")
        return

    print("--- Connecting to LIVE database... ---")
    # echo=True for more verbosity, useful for debugging SQL statements
    engine = create_async_engine(db_url, echo=True) 

    async with engine.begin() as conn:
        print("--- Creating all tables (if they don't exist)... ---")
        # Use checkfirst=True to avoid DuplicateTableError if tables/indexes already exist
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, checkfirst=True))
        print("--- Tables and indexes ensured to exist. ---")

    # Optional: Seed initial data or perform other setup tasks here
    # For example, to create the admin user if it doesn't exist:
    # async with AsyncSession(engine) as session:
    #     # You'll need to define your User model and a way to check for existing users
    #     from backend.app.models import User # Adjust import path for User model
    #     from sqlalchemy import select
    #     
    #     existing_admin = await session.execute(select(User).filter_by(username='admin'))
    #     if not existing_admin.scalar_one_or_none():
    #         # Create admin user
    #         # Ensure you have proper password hashing here, e.g., using bcrypt
    #         # For demonstration, 'your_hashed_password' is a placeholder
    #         admin_user = User(
    #             username='admin', 
    #             password_hash='your_hashed_password', # Replace with a properly hashed password
    #             full_name='Admin User', 
    #             role='admin'
    #         )
    #         session.add(admin_user)
    #         await session.commit()
    #         print("Admin user created.")
    #     else:
    #         print("Admin user already exists.")

    # Dispose of the engine to close all connections in the pool
    await engine.dispose()
    print("--- Database setup complete. ---")

if __name__ == "__main__":
    asyncio.run(main())