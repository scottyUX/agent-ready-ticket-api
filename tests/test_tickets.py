"""Behavioral tests for the public ticket API."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repository import ticket_repository


@pytest.fixture(autouse=True)
def reset_ticket_storage() -> None:
    """Clear in-memory tickets so tests do not depend on execution order."""
    ticket_repository.reset()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def test_create_ticket_returns_open_ticket(client: TestClient) -> None:
    # Arrange
    payload = {
        "title": "  Printer jam  ",
        "description": "  The lab printer is jammed.  ",
    }

    # Act
    response = client.post("/tickets", json=payload)

    # Assert
    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "title", "description", "status"}
    assert body["id"] == 1
    assert body["title"] == "Printer jam"
    assert body["description"] == "The lab printer is jammed."
    assert body["status"] == "open"


@pytest.mark.parametrize("field", ["title", "description"])
def test_create_ticket_rejects_blank_text(client: TestClient, field: str) -> None:
    # Arrange
    payload = {
        "title": "Printer jam",
        "description": "The lab printer is jammed.",
    }
    payload[field] = "   "

    # Act
    response = client.post("/tickets", json=payload)

    # Assert
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert field in detail
    assert "Traceback" not in detail


def test_create_ticket_rejects_missing_description(client: TestClient) -> None:
    # Arrange
    payload = {"title": "Printer jam"}

    # Act
    response = client.post("/tickets", json=payload)

    # Assert
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert "description" in detail
    assert "Traceback" not in detail


def test_create_ticket_rejects_title_over_120_characters(client: TestClient) -> None:
    # Arrange
    payload = {"title": "x" * 121, "description": "Too long."}

    # Act
    response = client.post("/tickets", json=payload)

    # Assert
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)


def test_list_tickets_is_empty_at_start(client: TestClient) -> None:
    # Act
    response = client.get("/tickets")

    # Assert
    assert response.status_code == 200
    assert response.json() == []


def test_list_tickets_returns_created_tickets_in_order(client: TestClient) -> None:
    # Arrange
    client.post(
        "/tickets",
        json={"title": "Printer jam", "description": "Paper is stuck."},
    )
    client.post(
        "/tickets",
        json={"title": "Login help", "description": "Cannot sign in."},
    )

    # Act
    response = client.get("/tickets")

    # Assert
    assert response.status_code == 200
    titles = [ticket["title"] for ticket in response.json()]
    assert titles == ["Printer jam", "Login help"]


def test_get_ticket_returns_one_ticket(client: TestClient) -> None:
    # Arrange
    created = client.post(
        "/tickets",
        json={"title": "Login help", "description": "Cannot sign in."},
    )

    # Act
    response = client.get(f"/tickets/{created.json()['id']}")

    # Assert
    assert created.status_code == 201
    assert created.json()["id"] == 1
    assert response.status_code == 200
    assert response.json() == created.json()


def test_get_missing_ticket_returns_not_found(client: TestClient) -> None:
    # Act
    response = client.get("/tickets/99")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Ticket not found."}


def test_get_ticket_rejects_non_numeric_id(client: TestClient) -> None:
    # Act
    response = client.get("/tickets/not-a-number")

    # Assert
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert "ticket_id" in detail
    assert "Traceback" not in detail


def test_update_status_returns_updated_ticket(client: TestClient) -> None:
    # Arrange
    created = client.post(
        "/tickets",
        json={"title": "Printer jam", "description": "Paper is stuck."},
    ).json()

    # Act
    response = client.patch(
        f"/tickets/{created['id']}",
        json={"status": "in_progress"},
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["title"] == "Printer jam"
    assert body["status"] == "in_progress"
    assert client.get(f"/tickets/{created['id']}").json()["status"] == "in_progress"


def test_update_missing_ticket_returns_not_found(client: TestClient) -> None:
    # Act
    response = client.patch("/tickets/99", json={"status": "resolved"})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Ticket not found."}


def test_update_status_rejects_unknown_value(client: TestClient) -> None:
    # Arrange
    created = client.post(
        "/tickets",
        json={"title": "Printer jam", "description": "Paper is stuck."},
    ).json()

    # Act
    response = client.patch(
        f"/tickets/{created['id']}",
        json={"status": "closed"},
    )

    # Assert
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert "status" in detail
    assert "Traceback" not in detail
    assert client.get(f"/tickets/{created['id']}").json()["status"] == "open"
