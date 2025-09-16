from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import asyncio

from .config import settings
from .db import engine, get_db
from .models import Base
from .api import v1  # Import your API router

app = FastAPI(title="Coimbatore Caterers CRM", version="1.0.0")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler for rate limits
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded"}
    )

# Include API router
app.include_router(v1.router, prefix="/api/v1", tags=["Leads"])


# --------------------------
# Async table creation
# --------------------------
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Run table creation at startup
@app.on_event("startup")
async def on_startup():
    await init_models()