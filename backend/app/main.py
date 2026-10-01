import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

# ── Logging must be configured before anything imports logger ──
from app.core.logging import configure_logging
configure_logging()

from loguru import logger
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from app.core.database import Base, engine, SessionLocal
from app.models.traffic import Violation, FineByState, LawSection
from app.models.chat_history import ChatHistory, ChatSession
from app.models.user import User
from app.core.seeder import seed_database
from app.core.rate_limit import limiter, RateLimitExceeded, _rate_limit_exceeded_handler
from app.config import settings

# ── Create all tables ──
Base.metadata.create_all(bind=engine)

# ── Seed lookup data ──
db = SessionLocal()
try:
    seed_database(db)
    logger.info("Database seeded successfully")
except Exception as e:
    logger.error(f"Seeding failed: {e}")
finally:
    db.close()

# ── App ──
app = FastAPI(
    title="Pothprohori RAG API",
    version="1.0.0",
    description="AI-powered Indian traffic law assistant",
)

# ── Rate limiting ──
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / response logging middleware ──
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"→ {request.method} {request.url.path} | ip={request.client.host}")
    try:
        response = await call_next(request)
        logger.info(f"← {request.method} {request.url.path} | status={response.status_code}")
        return response
    except Exception as exc:
        logger.exception(f"Unhandled error on {request.url.path}: {exc}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# ── Routers ──
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

@app.get("/health", tags=["health"])
def health():
    logger.debug("Health check called")
    return {"status": "ok", "version": "1.0.0"}
