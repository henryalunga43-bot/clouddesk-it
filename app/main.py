
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


if __name__ == "__main__":
    app.run(debug=True)
