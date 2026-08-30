import pytest

from app import create_app


@pytest.fixture
def client():
    application = create_app()
    application.config.update(TESTING=True)
    return application.test_client()


def test_exact_route_contract(client):
    routes = {
        (rule.rule, tuple(sorted(rule.methods - {"HEAD", "OPTIONS"})))
        for rule in client.application.url_map.iter_rules()
        if rule.endpoint != "static"
    }
    assert routes == {
        ("/health", ("GET",)),
        ("/info", ("GET",)),
        ("/echo", ("POST",)),
        ("/items/<int:item_id>", ("GET",)),
        ("/slow", ("GET",)),
    }


def test_health_is_immediate(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_info(client):
    response = client.get("/info")

    assert response.status_code == 200
    assert response.get_json() == {"framework": "flask", "profile": "light"}


def test_echo_round_trip(client):
    response = client.post("/echo", json={"message": "hello", "count": 2})

    assert response.status_code == 200
    assert response.get_json() == {"received": {"message": "hello", "count": 2}}


@pytest.mark.parametrize(
    "payload",
    [None, [], {}, {"message": "", "count": 1}, {"message": "hello", "count": True}],
)
def test_echo_rejects_invalid_json(client, payload):
    response = client.post("/echo", json=payload)

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_item_path_and_query_parameters(client):
    response = client.get("/items/7?include_details=true")

    assert response.status_code == 200
    assert response.get_json() == {
        "details": "Reference item 7",
        "include_details": True,
        "item_id": 7,
    }


@pytest.mark.parametrize("path", ["/items/0", "/items/7?include_details=maybe"])
def test_item_rejects_invalid_parameters(client, path):
    response = client.get(path)

    assert response.status_code == 400


def test_slow_uses_exact_duration_without_waiting(client, monkeypatch):
    observed = []
    monkeypatch.setattr("app.routes.sleep", observed.append)

    response = client.get("/slow")

    assert response.status_code == 200
    assert observed == [80]
    assert response.get_json() == {"delay_seconds": 80, "status": "completed"}
