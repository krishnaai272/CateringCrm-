from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from .db import get_db

app = FastAPI(title="Database Connection Test")

@app.get("/")
async def root(db: AsyncSession = Depends(get_db)):
    try:
        # A simple query to test the connection and see if tables exist
        print("--- Testing database connection and querying for 'users' table ---")
        result = await db.execute(text("SELECT 1 FROM users LIMIT 1"))
        print("--- Query successful! 'users' table exists. ---")
        return {"database_connection": "successful", "users_table": "found"}
    except Exception as e:
        print(f"🔴 ERROR: Query failed. The 'users' table likely does not exist.")
        print(e)
        return {"database_connection": "successful", "users_table": "NOT found", "error": str(e)}


# -------------------------
# Startup event - The Final, Simplest Version
# -------------------------
