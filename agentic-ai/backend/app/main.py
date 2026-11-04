from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import settings
from app.services.progress import broker
import asyncio

from app.db.mongo import get_db
from app.db.init_db import ensure_collections
from app.services.seed_insight_vault import verify_or_seed

from app.api.routes.health import router as health_router
from app.api.routes.vault import router as vault_router
from app.api.routes.uia import router as uia_router
from app.api.routes.auth import router as auth_router
from app.api.routes.chats import router as chats_router
from app.api.routes.messages import router as messages_router
from app.api.routes.chat import router as chat_state_router
from app.api.routes.insights import router as insights_router


app = FastAPI(title=settings.APP_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$" if settings.ENV.lower() in ("dev", "development", "test") else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz", include_in_schema=False)
async def healthz():
    await get_db().command("ping")
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    db = get_db()
    await ensure_collections(db)
    await verify_or_seed(db)
    asyncio.create_task(broker.gc_loop())

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(chats_router)
app.include_router(messages_router)
app.include_router(vault_router)
app.include_router(uia_router)
app.include_router(chat_state_router)
app.include_router(insights_router)