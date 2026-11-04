import uuid


def test_signup_rejects_short_password(client):
    r = client.post("/auth/signup", json={"email": f"{uuid.uuid4().hex[:8]}@example.com", "password": "short"})
    assert r.status_code == 422


def test_signin_wrong_password(client, user_a):
    # user_a's email is not exposed, so create a fresh account to sign in against
    email = f"{uuid.uuid4().hex[:8]}@example.com"
    client.post("/auth/signup", json={"email": email, "password": "password123"})
    assert client.post("/auth/signin", json={"email": email, "password": "wrong-password"}).status_code == 401
    assert client.post("/auth/signin", json={"email": email, "password": "password123"}).status_code == 200


def test_access_token_cannot_be_used_to_refresh(client, user_a):
    r = client.post("/auth/refresh", json={"refresh_token": user_a["access_token"]})
    assert r.status_code == 401


def test_refresh_rotates_and_old_token_is_revoked(client, user_a):
    old = user_a["refresh_token"]
    r = client.post("/auth/refresh", json={"refresh_token": old})
    assert r.status_code == 200
    assert client.post("/auth/refresh", json={"refresh_token": old}).status_code == 401


def test_protected_routes_require_token(client):
    assert client.get("/chats").status_code == 401
    assert client.post("/uia/intake", json={"chat_id": "x", "user_message": "hi"}).status_code == 401
    assert client.get("/chats/abc/uia-state").status_code == 401
