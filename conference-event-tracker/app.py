# Copyright 2026 Google LLC
"""
Flask web server for the Conference Event Tracker.

This server exposes routes for rendering the web application UI and API
endpoints for retrieving and creating conference events. It implements
input validation, secure HTTP headers, and error handling.
"""

from datetime import datetime
import os
import secrets
from flask import Flask, jsonify, render_template, request, Response
from loguru import logger
import database

# Initialize Flask app
app = Flask(__name__)

# Secure secret key generation (Environment-first with secure fallback)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
if not app.secret_key:
    logger.warning("Generating ephemeral secret key. Session state will not persist across restarts.")
    app.secret_key = secrets.token_hex(32)

# Ensure database is initialized
database.init_db()

# Allowed categories for event classification
ALLOWED_CATEGORIES = {"Keynote", "Tech Talk", "Workshop", "Panel"}


@app.after_request
def apply_security_headers(response: Response) -> Response:
    """
    Applies security headers to every outgoing HTTP response.

    Args:
        response (Response): The original response object.

    Returns:
        Response: The modified response with security headers.
    """
    # Strict Content Security Policy allowing only local resources
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "object-src 'none'; "
        "frame-ancestors 'none';"
    )
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    # Prevent mime type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Referrer policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.route("/", methods=["GET"])
def index() -> str:
    """
    Serves the primary Single-Page Application (SPA) HTML interface.
    """
    return render_template("index.html")


@app.route("/api/events", methods=["GET"])
def get_events() -> Response:
    """
    API endpoint to retrieve all conference events.

    Returns:
        Response: JSON array of events sorted by start time.
    """
    try:
        events = database.get_events()
        return jsonify(events)
    except Exception:
        logger.exception("Failed to retrieve events")
        return jsonify({"error": "An internal error occurred while fetching events."}), 500


@app.route("/api/events", methods=["POST"])
def add_event() -> Response:
    """
    API endpoint to add a new event to the conference schedule.
    Validates input parameters securely before database insertion.

    Returns:
        Response: JSON status representing success or error message.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request payload. Expected JSON."}), 400

    # Extract fields and strip whitespace
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    speaker = str(data.get("speaker", "")).strip()
    location = str(data.get("location", "")).strip()
    category = str(data.get("category", "")).strip()
    start_time_raw = str(data.get("start_time", "")).strip()
    end_time_raw = str(data.get("end_time", "")).strip()

    # Validate non-empty fields
    errors = []
    if not title:
        errors.append("Title is required.")
    if not description:
        errors.append("Description is required.")
    if not speaker:
        errors.append("Speaker name is required.")
    if not location:
        errors.append("Location/Room is required.")

    # Validate category against allowed set
    if category not in ALLOWED_CATEGORIES:
        errors.append(f"Category must be one of: {', '.join(ALLOWED_CATEGORIES)}")

    # Parse and validate times
    start_time = None
    end_time = None
    try:
        start_time = datetime.fromisoformat(start_time_raw)
    except ValueError:
        errors.append("Start time must be a valid ISO 8601 datetime format (YYYY-MM-DDTHH:MM).")

    try:
        end_time = datetime.fromisoformat(end_time_raw)
    except ValueError:
        errors.append("End time must be a valid ISO 8601 datetime format (YYYY-MM-DDTHH:MM).")

    if start_time and end_time and end_time <= start_time:
        errors.append("End time must be after the start time.")

    if errors:
        return jsonify({"errors": errors}), 400

    # Insert into database using parameterized query inside database module
    try:
        new_id = database.add_event(
            title=title,
            description=description,
            speaker=speaker,
            location=location,
            category=category,
            start_time=start_time_raw,
            end_time=end_time_raw,
        )
        logger.info("Successfully added event ID: {}", new_id)
        return jsonify({"message": "Event created successfully.", "id": new_id}), 201
    except Exception:
        logger.exception("Failed to add event")
        return jsonify({"error": "An internal error occurred while saving the event."}), 500


if __name__ == "__main__":
    # Ensure Flask binds to localhost for secure local testing
    # Load debug setting from environment, default to False for security
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(host="127.0.0.1", port=5000, debug=debug_mode)
