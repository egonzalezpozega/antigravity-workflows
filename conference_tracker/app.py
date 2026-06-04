# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Main Flask application and routing file for the Conference Event Tracker.

This file sets up the Flask application, initializes the database, configures
session security, enforces CSRF validation on all state-changing requests,
performs robust input validation, and serves the application routes.
"""

import os
import secrets
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for, flash, session, abort
)
from loguru import logger
from database import db, Event


def get_secret_key() -> str:
    """Retrieves the Flask secret key using a multi-tiered fallback.

    Resolution:
    1. Check for 'SECRET_KEY' environment variable.
    2. Check for a local 'secret.txt' file.
    3. Generate a secure, ephemeral random token (logs a severe warning).
    """
    if os.getenv('SECRET_KEY'):
        logger.info("Using secret key from environment variable.")
        return os.getenv('SECRET_KEY')

    secret_file = os.path.join(os.path.dirname(__file__), 'secret.txt')
    if os.path.exists(secret_file):
        try:
            with open(secret_file, 'r', encoding='utf-8') as f:
                key = f.read().strip()
                if key:
                    logger.info("Using secret key from local file.")
                    return key
        except IOError as e:
            logger.error("Failed to read secret.txt: {}", e)

    # Ephemeral fallback
    logger.warning("Generating ephemeral secret. Instance-isolated! Session persistence will not survive restarts.")
    return secrets.token_hex(32)


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = get_secret_key()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conference.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure secure session cookie flags
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production (HTTPS)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize database
db.init_app(app)


# --- Custom CSRF Protection Handler ---

@app.before_request
def csrf_protect():
    """Enforces CSRF token validation on all state-changing (POST) requests.

    Each GET request ensures a token is in the session. Any POST request
    must submit a 'csrf_token' field that matches the session token.
    """
    # Ensure CSRF token exists in session
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)

    # Validate CSRF on state-changing requests
    if request.method == "POST":
        token_in_form = request.form.get('csrf_token')
        token_in_session = session.get('csrf_token')

        if not token_in_form or not token_in_session or not secrets.compare_digest(token_in_form, token_in_session):
            logger.warning("CSRF validation failed! IP: {}", request.remote_addr)
            abort(400, "CSRF token validation failed. Please refresh and try again.")


@app.context_processor
def inject_csrf_token():
    """Injects the CSRF token into all template contexts automatically."""
    return dict(csrf_token=session.get('csrf_token'))


# --- Security HTTP Headers ---

@app.after_request
def add_security_headers(response):
    """Appends security-related HTTP response headers."""
    # Prevent browser mime-sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # Modern Content Security Policy (CSP)
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "style-src 'self' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "script-src 'self'; "
        "img-src 'self' data:; "
        "frame-ancestors 'self';"
    )
    return response


# --- Application Routes ---

@app.route('/')
def index():
    """Renders the main dashboard showing all upcoming conference events."""
    try:
        # Retrieve all events, sorted chronologically by date and then time
        events = Event.query.order_order_by_desc = False
        events = Event.query.order_by(Event.date.asc(), Event.time.asc()).all()
        return render_template('index.html', events=events)
    except Exception as e:
        logger.error("Error retrieving events from database: {}", e)
        # Fail secure: do not leak raw SQL errors to users
        return render_template('index.html', events=[], error="An unexpected database error occurred.")


@app.route('/add-event', methods=['GET', 'POST'])
def add_event():
    """Handles displaying and processing the 'Add Event' form."""
    if request.method == 'POST':
        # 1. Extract form values
        title = request.form.get('title', '').strip()
        speaker = request.form.get('speaker', '').strip()
        date_str = request.form.get('date', '').strip()
        time_str = request.form.get('time', '').strip()
        location = request.form.get('location', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()

        errors = []

        # 2. Input Validation (Treat all inputs as untrusted and validate schema)
        if not title or len(title) > 150:
            errors.append("Title is required and must be under 150 characters.")
        if not speaker or len(speaker) > 100:
            errors.append("Speaker/Organizer name is required and must be under 100 characters.")
        if not date_str:
            errors.append("Event date is required.")
        if not time_str:
            errors.append("Event start time is required.")
        if not location or len(location) > 100:
            errors.append("Location is required and must be under 100 characters.")
        if not category or category not in ['Keynote', 'Workshop', 'Panel', 'Networking']:
            errors.append("Invalid or missing category selection.")
        if len(description) > 1000:
            errors.append("Description is too long (maximum 1000 characters).")

        # 3. Parse and validate date and time format
        parsed_date = None
        parsed_time = None

        if date_str:
            try:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                errors.append("Invalid date format. Use YYYY-MM-DD.")

        if time_str:
            try:
                parsed_time = datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                errors.append("Invalid time format. Use HH:MM.")

        # 4. If there are validation errors, re-render form with details
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('add_event.html', form_data=request.form)

        # 5. Save to database using parameterized insert (via SQLAlchemy ORM)
        try:
            new_event = Event(
                title=title,
                speaker=speaker,
                date=parsed_date,
                time=parsed_time,
                location=location,
                category=category,
                description=description if description else None
            )
            db.session.add(new_event)
            db.session.commit()
            flash(f"Successfully added event: '{title}'!", 'success')
            logger.info("Successfully added new conference event: {} (ID: {})", title, new_event.id)
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            logger.error("Failed to insert event into database: {}", e)
            # Fail secure: log details privately, present generic error to user
            flash("A secure database error occurred. Your event could not be saved.", 'danger')
            return render_template('add_event.html', form_data=request.form)

    # GET Request: render form
    return render_template('add_event.html', form_data={})


if __name__ == '__main__':
    # Strictly bind to 127.0.0.1 (localhost) and run on port 5000
    # Enable debug mode only if FLASK_DEBUG is explicitly set to '1' or 'true'
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() in ('true', '1')
    app.run(host='127.0.0.1', port=5000, debug=debug_mode)
