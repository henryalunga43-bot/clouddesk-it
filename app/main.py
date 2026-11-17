
from flask import Flask, jsonify

app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(debug=True)
