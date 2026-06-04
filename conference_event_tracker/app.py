# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Conference Event Tracker Application

A highly secure, premium web application built with Flask and SQLite to track,
manage, and view conference events and sessions.

Author: Antigravity AI
"""

import os
import sqlite3
import secrets
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, abort, g, flash
from loguru import logger

app = Flask(__name__)

# Secure Session Management: Generate a cryptographically strong, random secret key
def get_secret_key():
    """Resolves secret key from environment variables or creates an ephemeral key."""
    if os.getenv('SECRET_KEY'):
        return os.getenv('SECRET_KEY')
    
    # Check if a saved secret key exists locally
    secret_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'session_secret.txt')
    if os.path.exists(secret_file):
        try:
            with open(secret_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except IOError:
            logger.error("Failed to read stored secret key.")
            
    # Generate an ephemeral secret key (fail close to localized, instance-isolated memory)
    logger.warning("Generating ephemeral session secret. Active sessions will invalidate on restart!")
    ephemeral_key = secrets.token_hex(32)
    try:
        with open(secret_file, 'w', encoding='utf-8') as f:
            f.write(ephemeral_key)
    except IOError:
        logger.warning("Could not write ephemeral secret to disk.")
    return ephemeral_key

app.secret_key = get_secret_key()

# Database Configuration
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'events.db')

def get_db():
    """Provides a thread-safe database connection using Flask context globals."""
    db = getattr(g, '_database', None)
    if db is None:
        try:
            db = g._database = sqlite3.connect(DATABASE_PATH)
            db.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            logger.critical(f"Database connection error: {str(e)}")
            abort(500, description="Internal system error. Please contact administrative support.")
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Safely closes the SQLite connection at the end of the request lifecycle."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database schema and pre-populates default conference tracks."""
    with app.app_context():
        try:
            db = get_db()
            db.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    speaker TEXT NOT NULL,
                    category TEXT NOT NULL,
                    event_date TEXT NOT NULL,
                    event_time TEXT NOT NULL,
                    location TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.commit()
            
            # Check if empty, and pre-populate some high-quality sample events
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(*) FROM events")
            if cursor.fetchone()[0] == 0:
                logger.info("Pre-populating database with premium default conference sessions.")
                sample_events = [
                    (
                        "Generative AI Frontiers in Enterprise",
                        "Explore the latest paradigms in transformer architectures, fine-tuning techniques, and safety guardrails for production environments.",
                        "Dr. Elena Rostova",
                        "AI & Deep Learning",
                        "2026-06-15",
                        "09:30",
                        "Main Auditorium (Hall A)"
                    ),
                    (
                        "Zero Trust Security in Cloud Native Environments",
                        "A deep dive into mutual TLS, decentralized identity assertion, and containerized workload isolation in modern Kubernetes fleets.",
                        "Marcus Vance",
                        "Cybersecurity",
                        "2026-06-15",
                        "11:00",
                        "Security Theatre (Hall C)"
                    ),
                    (
                        "Symphonies of Scale: Advanced Web Architectures",
                        "Discover how modern distributed edge computing, custom rendering trees, and real-time streams deliver premium microsecond responses.",
                        "Sarah Jenkins",
                        "Web Development",
                        "2026-06-16",
                        "14:00",
                        "Vanguard Stage (Hall B)"
                    )
                ]
                db.executemany("""
                    INSERT INTO events (title, description, speaker, category, event_date, event_time, location)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, sample_events)
                db.commit()
        except sqlite3.Error as e:
            logger.critical(f"Database initialization failed: {str(e)}")
            raise

# --- Security Mitigations ---

# CSRF Mitigation: Double Submit/Synchronizer Token implementation
def generate_csrf_token():
    """Generates and sets a cryptographically secure session-backed CSRF token."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

@app.before_request
def validate_csrf():
    """Validates the CSRF token on all state-changing requests."""
    if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        # Fetch token from standard form input or request header
        token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
        expected_token = session.get('csrf_token')
        
        if not expected_token or not token or not secrets.compare_digest(expected_token, token):
            logger.warning("CSRF check failed: invalid or missing token.")
            abort(403, description="Access Denied: Invalid security context (CSRF failure).")

# Response Security Headers
@app.after_request
def enforce_security_headers(response):
    """Injects mandatory secure headers to protect the client and mitigate attack surfaces."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Strict Content Security Policy (CSP): Allow self source, restrict CDNs, allow safe Google Font schemas
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "script-src 'self'; "
        "frame-ancestors 'none';"
    )
    return response

# Custom Safe Error Handlers to avoid leaking engine error states
@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error.html', error_title="403 Forbidden", error_message=str(error.description)), 403

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_title="404 Not Found", error_message="The requested conference page could not be located."), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html', error_title="500 Server Error", error_message="An internal engine failure occurred. Our developers have been notified."), 500


# --- Web Routes ---

@app.route('/')
def index():
    """Renders the dashboard landing page containing event list, analytics, and stats."""
    try:
        db = get_db()
        # Retrieve all events ordered by date and time
        cursor = db.execute("SELECT * FROM events ORDER BY event_date ASC, event_time ASC")
        events = cursor.fetchall()
        
        # Calculate stats for dashboard highlights
        total_events = len(events)
        
        # Extract unique categories from db results
        categories = sorted(list(set(event['category'] for event in events)))
        
        # Find count of events occurring today or in the future
        current_date_str = datetime.now().strftime("%Y-%m-%d")
        upcoming_count = sum(1 for event in events if event['event_date'] >= current_date_str)
        
        return render_template(
            'index.html',
            events=events,
            total_events=total_events,
            categories=categories,
            upcoming_count=upcoming_count,
            current_date=current_date_str
        )
    except sqlite3.Error as e:
        logger.error(f"Failed to query events: {str(e)}")
        abort(500)

@app.route('/add', methods=['GET', 'POST'])
def add_event():
    """Renders and processes the new conference event registration form."""
    if request.method == 'POST':
        # Retrieve and sanitize form inputs
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        speaker = request.form.get('speaker', '').strip()
        category = request.form.get('category', '').strip()
        event_date = request.form.get('event_date', '').strip()
        event_time = request.form.get('event_time', '').strip()
        location = request.form.get('location', '').strip()
        
        # Strict Input Validation
        errors = []
        if not title or len(title) < 5 or len(title) > 100:
            errors.append("Title must be between 5 and 100 characters long.")
        if not description or len(description) < 10 or len(description) > 1000:
            errors.append("Description must be between 10 and 1000 characters.")
        if not speaker or len(speaker) < 2 or len(speaker) > 80:
            errors.append("Speaker name must be between 2 and 80 characters.")
        if not category or len(category) < 2 or len(category) > 50:
            errors.append("Please specify a valid category (2-50 characters).")
        if not location or len(location) < 3 or len(location) > 100:
            errors.append("Location must be specified (3-100 characters).")
            
        # Date & Time Format Validation
        try:
            datetime.strptime(event_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Invalid date format. Expected YYYY-MM-DD.")
            
        try:
            datetime.strptime(event_time, "%H:%M")
        except ValueError:
            errors.append("Invalid time format. Expected HH:MM.")
            
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template('add_event.html'), 400
            
        try:
            # Secure Parameterized Writing to Database (Completely prevents SQLi)
            db = get_db()
            db.execute("""
                INSERT INTO events (title, description, speaker, category, event_date, event_time, location)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, description, speaker, category, event_date, event_time, location))
            db.commit()
            
            flash("Success! The new conference session was added securely.", "success")
            return redirect(url_for('index'))
            
        except sqlite3.Error as e:
            logger.error(f"Failed to insert new event: {str(e)}")
            flash("A technical database exception occurred while saving the event.", "danger")
            return render_template('add_event.html'), 500
            
    # GET request: render empty event submission form
    return render_template('add_event.html')

if __name__ == '__main__':
    # Initialize the tables and prepopulate if required
    init_db()
    # MUST listen on localhost (127.0.0.1) for testing. Never listen on 0.0.0.0.
    app.run(host='127.0.0.1', port=5000, debug=True)
