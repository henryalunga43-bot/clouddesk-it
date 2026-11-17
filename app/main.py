
from datetime import datetime, timezone
from flask import Flask, jsonify, request

app = Flask(__name__)

# Temporary in-memory ticket storage.
# Persistent Azure storage will be added later.
tickets = []


@app.get("/")
def home():
    return jsonify({
        "application": "CloudDesk IT",
        "message": "IT Support Ticketing API",
        "version": "1.0.0"
    })


@app.get("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "clouddesk-it"
    })


@app.post("/api/tickets")
def create_ticket():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A JSON object is required"
        }), 400

    required_fields = [
        "title",
        "description",
        "priority",
        "category",
        "requested_by"
    ]

    for field in required_fields:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return jsonify({
                "error": f"{field} is required"
            }), 400

    priority = data["priority"].strip().lower()

    if priority not in ["low", "medium", "high", "critical"]:
        return jsonify({
            "error": "Invalid priority"
        }), 400

    ticket = {
        "id": f"TCK-{len(tickets) + 1:04d}",
        "title": data["title"].strip(),
        "description": data["description"].strip(),
        "priority": priority,
        "category": data["category"].strip(),
        "requested_by": data["requested_by"].strip(),
        "status": "open",
        "assigned_to": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    tickets.append(ticket)

    return jsonify(ticket), 201


@app.get("/api/tickets")
def get_tickets():
    return jsonify({
        "count": len(tickets),
        "tickets": tickets
    }), 200



@app.patch("/api/tickets/<ticket_id>/status")
def update_ticket_status(ticket_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A JSON object is required"
        }), 400

    new_status = data.get("status")

    allowed_statuses = [
        "open",
        "in_progress",
        "resolved",
        "closed"
    ]

    if not isinstance(new_status, str):
        return jsonify({
            "error": "Status must be a string"
        }), 400

    new_status = new_status.strip().lower()

    if new_status not in allowed_statuses:
        return jsonify({
            "error": "Invalid ticket status",
            "allowed_statuses": allowed_statuses
        }), 400

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket["status"] = new_status
            ticket["updated_at"] = (
                datetime.now(timezone.utc).isoformat()
            )

            return jsonify({
                "message": "Ticket status updated",
                "ticket": ticket
            }), 200

    return jsonify({
        "error": "Ticket not found"
    }), 404


@app.patch("/api/tickets/<ticket_id>/assign")
def assign_ticket(ticket_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A JSON object is required"
        }), 400

    technician = data.get("assigned_to")

    if not isinstance(technician, str) or not technician.strip():
        return jsonify({
            "error": "assigned_to must be a non-empty string"
        }), 400

    technician = technician.strip()

    if len(technician) > 100:
        return jsonify({
            "error": "assigned_to must be 100 characters or fewer"
        }), 400

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket["assigned_to"] = technician
            ticket["updated_at"] = (
                datetime.now(timezone.utc).isoformat()
            )

            return jsonify({
                "message": "Ticket assigned successfully",
                "ticket": ticket
            }), 200

    return jsonify({
        "error": "Ticket not found"
    }), 404


if __name__ == "__main__":
    app.run(debug=True)
