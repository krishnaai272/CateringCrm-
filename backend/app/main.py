from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

# --- These are the essential imports for your application ---
from .config import settings
from .api import v1  # This imports your router with all the endpoints

# -------------------------
# FastAPI app
# -------------------------
app = FastAPI(title="Coimbatore Caterers CRM", version="1.0.0")

# Rate limiter (if you are using it)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# CORS middleware - reads the allowed origins from your settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limit exception handler (if you are using it)
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded"}
    )

# Include your API router, which contains all the endpoints (/leads, /auth/login, etc.)
# This is where your application's logic lives.
app.include_router(v1.router, prefix="/api/v1")


# --- NO on_startup EVENT ---
# The database and user setup is now a separate, manual step.
# This makes the application startup clean, fast, and reliable.
# A simple health-check endpoint can be useful.
@app.get("/", tags=["Health Check"])
def root():
    return {"status": "ok", "message": "Catering CRM API is running."}