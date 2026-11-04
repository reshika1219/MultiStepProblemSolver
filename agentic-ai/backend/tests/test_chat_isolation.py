"""A user must not be able to read or modify another user's chat through any route."""


def test_uia_state_is_owner_only(client, user_a, user_b, chat_a):
    assert client.get(f"/chats/{chat_a}/uia-state", headers=user_a["headers"]).status_code == 200
    assert client.get(f"/chats/{chat_a}/uia-state", headers=user_b["headers"]).status_code == 404


def test_uia_submit_is_owner_only(client, user_b, chat_a):
    body = {"chat_id": chat_a, "employment_category_id": "ec_ds", "vault_version": "2025-10-11#1"}
    assert client.post("/uia/submit/employment", json=body, headers=user_b["headers"]).status_code == 404


def test_intake_is_owner_only(client, user_b, chat_a):
    r = client.post("/uia/intake", json={"chat_id": chat_a, "user_message": "hi"}, headers=user_b["headers"])
    assert r.status_code == 404


def test_insights_are_owner_only(client, user_b, chat_a):
    assert client.get(f"/insights/pending/{chat_a}", headers=user_b["headers"]).status_code == 404
    r = client.post("/insights/auto-infer", json={"chatId": chat_a, "text": "hi"}, headers=user_b["headers"])
    assert r.status_code == 404


def test_messages_are_owner_only(client, user_b, chat_a):
    assert client.get(f"/messages/{chat_a}", headers=user_b["headers"]).status_code == 404
    assert client.patch(f"/chats/{chat_a}", json={"title": "x"}, headers=user_b["headers"]).status_code == 404
    assert client.delete(f"/chats/{chat_a}", headers=user_b["headers"]).status_code == 404


def test_malformed_chat_id_is_404_not_500(client, user_a):
    h = user_a["headers"]
    assert client.get("/messages/not-an-object-id", headers=h).status_code == 404
    assert client.get("/chats/not-an-object-id/uia-state", headers=h).status_code == 404
    assert client.patch("/chats/not-an-object-id", json={"title": "x"}, headers=h).status_code == 404
    assert client.delete("/chats/not-an-object-id", headers=h).status_code == 404
