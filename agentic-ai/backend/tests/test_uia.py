VAULT = "2025-10-11#1"


def test_submit_employment_names_the_category_and_is_one_shot(client, user_a, chat_a):
    body = {"chat_id": chat_a, "employment_category_id": "ec_ds", "vault_version": VAULT}
    r = client.post("/uia/submit/employment", json=body, headers=user_a["headers"])
    assert r.status_code == 200, r.text
    assert "Data Scientist" in r.json()["action"]
    # second attempt must be refused
    assert client.post("/uia/submit/employment", json=body, headers=user_a["headers"]).status_code == 409


def test_submit_employment_unknown_category(client, user_a, chat_a):
    body = {"chat_id": chat_a, "employment_category_id": "ec_nope", "vault_version": VAULT}
    assert client.post("/uia/submit/employment", json=body, headers=user_a["headers"]).status_code == 400


def test_submit_employment_stale_vault_version(client, user_a, chat_a):
    body = {"chat_id": chat_a, "employment_category_id": "ec_ds", "vault_version": "old"}
    assert client.post("/uia/submit/employment", json=body, headers=user_a["headers"]).status_code == 409
