
import pytest

from app.main import app, tickets


@pytest.fixture
def client():
    app.config["TESTING"] = True

    # Start every test with an empty ticket list.
    tickets.clear()

    with app.test_client() as test_client:
        yield test_client

    tickets.clear()


@pytest.fixture
def sample_ticket():
    return {
        "title": "VPN connection failure",
        "description": "Employee cannot connect to VPN",
        "priority": "high",
        "category": "Network",
        "requested_by": "test.employee@example.com"
    }


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_create_ticket(client, sample_ticket):
    response = client.post(
        "/api/tickets",
        json=sample_ticket
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] == "TCK-0001"
    assert data["title"] == "VPN connection failure"
    assert data["priority"] == "high"
    assert data["status"] == "open"
    assert data["assigned_to"] is None
    assert "created_at" in data


def test_get_tickets(client, sample_ticket):
    client.post("/api/tickets", json=sample_ticket)

    response = client.get("/api/tickets")

    assert response.status_code == 200

    data = response.get_json()

    assert data["count"] == 1
    assert len(data["tickets"]) == 1
    assert data["tickets"][0]["id"] == "TCK-0001"


def test_missing_required_field(client):
    response = client.post(
        "/api/tickets",
        json={
            "title": "Printer issue",
            "priority": "medium"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "description is required"
    )


def test_invalid_priority(client, sample_ticket):
    sample_ticket["priority"] = "urgent"

    response = client.post(
        "/api/tickets",
        json=sample_ticket
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "Invalid priority"
    )


def test_update_ticket_status(client, sample_ticket):
    client.post("/api/tickets", json=sample_ticket)

    response = client.patch(
        "/api/tickets/TCK-0001/status",
        json={"status": "in_progress"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["ticket"]["status"] == "in_progress"
    assert "updated_at" in data["ticket"]


def test_invalid_ticket_status(client, sample_ticket):
    client.post("/api/tickets", json=sample_ticket)

    response = client.patch(
        "/api/tickets/TCK-0001/status",
        json={"status": "waiting_forever"}
    )

    assert response.status_code == 400


def test_status_ticket_not_found(client):
    response = client.patch(
        "/api/tickets/TCK-9999/status",
        json={"status": "resolved"}
    )

    assert response.status_code == 404


def test_assign_ticket(client, sample_ticket):
    client.post("/api/tickets", json=sample_ticket)

    response = client.patch(
        "/api/tickets/TCK-0001/assign",
        json={"assigned_to": "Alex Morgan"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["ticket"]["assigned_to"] == "Alex Morgan"
    assert "updated_at" in data["ticket"]


def test_reassign_ticket(client, sample_ticket):
    client.post("/api/tickets", json=sample_ticket)

    client.patch(
        "/api/tickets/TCK-0001/assign",
        json={"assigned_to": "Alex Morgan"}
    )

    response = client.patch(
        "/api/tickets/TCK-0001/assign",
        json={"assigned_to": "Jordan Lee"}
    )

    assert response.status_code == 200
    assert response.get_json()["ticket"]["assigned_to"] == (
        "Jordan Lee"
    )


def test_invalid_assignment(client, sample_ticket):
    client.post("/api/tickets", json=sample_ticket)

    response = client.patch(
        "/api/tickets/TCK-0001/assign",
        json={"assigned_to": ""}
    )

    assert response.status_code == 400


def test_assignment_ticket_not_found(client):
    response = client.patch(
        "/api/tickets/TCK-9999/assign",
        json={"assigned_to": "Alex Morgan"}
    )

    assert response.status_code == 404
