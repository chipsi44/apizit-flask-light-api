import pytest

from app import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_summary(client):
    response = client.post("/api/v1/summary", json={"values": [1, 2, 3, 4]})

    assert response.status_code == 200
    assert response.get_json() == {
        "count": 4,
        "max": 4.0,
        "mean": 2.5,
        "median": 2.5,
        "min": 1.0,
        "percentile_25": 1.75,
        "percentile_75": 3.25,
        "population_std_dev": pytest.approx(1.118033988749895),
        "sum": 10.0,
    }


def test_normalize(client):
    response = client.post("/api/v1/normalize", json={"values": [10, 20, 30]})

    assert response.status_code == 200
    body = response.get_json()
    assert body["mean"] == 20.0
    assert body["values"] == pytest.approx([-1.224744871, 0.0, 1.224744871])


def test_normalize_constant_series(client):
    response = client.post("/api/v1/normalize", json={"values": [5, 5, 5]})

    assert response.status_code == 200
    assert response.get_json()["values"] == [0.0, 0.0, 0.0]


def test_correlation(client):
    response = client.post(
        "/api/v1/correlation",
        json={"x": [1, 2, 3], "y": [2, 4, 6]},
    )

    assert response.status_code == 200
    assert response.get_json() == {"coefficient": pytest.approx(1.0), "sample_size": 3}


def test_correlation_rejects_constant_series(client):
    response = client.post(
        "/api/v1/correlation",
        json={"x": [1, 1], "y": [2, 3]},
    )

    assert response.status_code == 422
    assert response.get_json() == {"error": "Correlation is undefined for a constant series."}


@pytest.mark.parametrize(
    "payload",
    [None, {}, {"values": []}, {"values": [1, True]}, {"values": [1, "2"]}],
)
def test_summary_rejects_invalid_payloads(client, payload):
    response = client.post("/api/v1/summary", json=payload)

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_correlation_requires_equal_length_series(client):
    response = client.post(
        "/api/v1/correlation",
        json={"x": [1, 2], "y": [1, 2, 3]},
    )

    assert response.status_code == 400
