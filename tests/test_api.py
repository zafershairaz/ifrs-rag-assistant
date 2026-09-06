from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert (
        data["application"]
        == "IFRS/IAS Research Assistant"
    )


def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_empty_question():

    response = client.post(
        "/ask",
        json={
            "question": ""
        }
    )

    assert response.status_code == 422


def test_short_question():

    response = client.post(
        "/ask",
        json={
            "question": "Hi"
        }
    )

    assert response.status_code == 422