import os
import uuid

import pytest

# Must be set before the app (and its settings) is imported.
os.environ["MONGO_DB"] = "agentic_ai_test"
os.environ.setdefault("ENV", "test")

from fastapi.testclient import TestClient  # noqa: E402
from pymongo import MongoClient  # noqa: E402

from app.core.settings import settings  # noqa: E402


def _mongo_available() -> bool:
    try:
        MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=1500).admin.command("ping")
        return True
    except Exception:
        return False


def _reset_motor():
    # Motor binds its client to the event loop it was first used on; drop the cached one.
    from app.db import mongo

    mongo._client = None
    mongo._db = None


@pytest.fixture(scope="session")
def client():
    if not _mongo_available():
        pytest.skip(f"MongoDB not reachable at {settings.MONGO_URI}")
    MongoClient(settings.MONGO_URI).drop_database("agentic_ai_test")

    import asyncio

    from scripts import seed_insight_vault, seed_vault

    # The app refuses to start without both vaults, so seed them first.
    asyncio.run(seed_vault.main())
    asyncio.run(seed_insight_vault.main())
    _reset_motor()

    from app.main import app

    with TestClient(app) as c:
        yield c
    _reset_motor()
    MongoClient(settings.MONGO_URI).drop_database("agentic_ai_test")


def _signup(client) -> dict:
    email = f"{uuid.uuid4().hex[:10]}@example.com"
    r = client.post("/auth/signup", json={"email": email, "password": "password123"})
    assert r.status_code == 200, r.text
    tokens = r.json()
    tokens["headers"] = {"Authorization": f"Bearer {tokens['access_token']}"}
    return tokens


@pytest.fixture()
def user_a(client):
    return _signup(client)


@pytest.fixture()
def user_b(client):
    return _signup(client)


@pytest.fixture()
def chat_a(client, user_a):
    r = client.post("/chats", json={"title": "A's chat"}, headers=user_a["headers"])
    assert r.status_code == 200, r.text
    return r.json()["id"]
