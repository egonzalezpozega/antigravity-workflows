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

"""Unit tests for the Conference Event Tracker.

This module uses pytest and Flask's test client to verify application routes,
database logic, robust input validation, and secure CSRF handling.
"""

import pytest
from datetime import date, time
from app import app, db
from database import Event


@pytest.fixture
def client():
    """Sets up an isolated Flask test client with an in-memory SQLite database."""
    from sqlalchemy import create_engine

    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'  # In-memory SQLite

    # Create and register a safe, in-memory SQLAlchemy engine to prevent dropping the physical DB
    engine = create_engine('sqlite://')
    app.extensions['sqlalchemy']._app_engines[app] = {None: engine}

    # Create the test client
    with app.test_client() as test_client:
        with app.app_context():
            db.create_all()
            yield test_client
            db.drop_all()


def test_index_route_empty(client):
    """Verifies that the index page displays correctly when there are no events."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Aura Events" in response.data
    assert b"No Events Found" in response.data


def test_index_route_with_events(client):
    """Verifies that the index page lists created events sorted chronologically."""
    with app.app_context():
        event1 = Event(
            title="Tech Panel",
            speaker="Alice",
            date=date(2026, 6, 20),
            time=time(14, 0),
            location="Room A",
            category="Panel",
            description="Discussing future tech."
        )
        event2 = Event(
            title="Opening Keynote",
            speaker="Bob",
            date=date(2026, 6, 20),
            time=time(9, 0),
            location="Grand Hall",
            category="Keynote",
            description="Welcoming everyone."
        )
        db.session.add(event1)
        db.session.add(event2)
        db.session.commit()

    response = client.get('/')
    assert response.status_code == 200
    assert b"Opening Keynote" in response.data
    assert b"Tech Panel" in response.data
    assert b'id="no-events-message" style="display: none;"' in response.data

    # Verify chronological sorting (Keynote at 9 AM should appear before Panel at 2 PM)
    html = response.data.decode('utf-8')
    keynote_idx = html.find("Opening Keynote")
    panel_idx = html.find("Tech Panel")
    assert keynote_idx < panel_idx


def test_add_event_get_route(client):
    """Verifies that the add-event form renders correctly and initiates a CSRF token."""
    response = client.get('/add-event')
    assert response.status_code == 200
    assert b"Register New Session" in response.data
    assert b"csrf_token" in response.data

    # Check that a CSRF token was populated in the session
    with client.session_transaction() as sess:
        assert 'csrf_token' in sess
        assert len(sess['csrf_token']) == 64


def test_add_event_post_success(client):
    """Verifies that submitting valid data with a valid CSRF token succeeds."""
    # First, GET the form to populate the session CSRF token
    client.get('/add-event')

    # Extract the generated CSRF token from the test client session
    with client.session_transaction() as sess:
        csrf_token = sess.get('csrf_token')

    # Post valid event data
    form_data = {
        'csrf_token': csrf_token,
        'title': 'New Workshop',
        'speaker': 'Dr. Vance',
        'date': '2026-06-18',
        'time': '10:30',
        'location': 'Auditorium C',
        'category': 'Workshop',
        'description': 'A very cool hands-on workshop.'
    }

    response = client.post('/add-event', data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Successfully added event: &#39;New Workshop&#39;!" in response.data or b"Successfully added event: 'New Workshop'!" in response.data
    assert b"New Workshop" in response.data

    # Confirm database state
    with app.app_context():
        saved_event = Event.query.filter_by(title="New Workshop").first()
        assert saved_event is not None
        assert saved_event.speaker == "Dr. Vance"
        assert saved_event.date == date(2026, 6, 18)
        assert saved_event.time == time(10, 30)
        assert saved_event.location == "Auditorium C"
        assert saved_event.category == "Workshop"


def test_add_event_post_csrf_failure(client):
    """Verifies that state-changing requests are aborted with a 400 error on CSRF failure."""
    # GET form to set up initial state
    client.get('/add-event')

    # Attempt to post without a CSRF token (fail-closed verification)
    form_data = {
        'title': 'Intruder Event',
        'speaker': 'Hacker',
        'date': '2026-06-18',
        'time': '10:30',
        'location': 'Unknown',
        'category': 'Workshop'
    }

    response = client.post('/add-event', data=form_data)
    assert response.status_code == 400
    assert b"CSRF token validation failed" in response.data

    # Check database to ensure no event was saved
    with app.app_context():
        intruder_event = Event.query.filter_by(title="Intruder Event").first()
        assert intruder_event is None


def test_add_event_validation_errors(client):
    """Verifies that invalid or missing form data triggers clear validation alerts."""
    client.get('/add-event')
    with client.session_transaction() as sess:
        csrf_token = sess.get('csrf_token')

    # Post invalid form data (missing title, invalid category)
    form_data = {
        'csrf_token': csrf_token,
        'title': '',  # Invalid (empty)
        'speaker': 'Alice',
        'date': '2026-06-18',
        'time': '10:30',
        'location': 'Auditorium C',
        'category': 'NotACategory'  # Invalid (not allowed)
    }

    response = client.post('/add-event', data=form_data)
    assert response.status_code == 200  # Renders form again
    assert b"Title is required" in response.data
    assert b"Invalid or missing category selection" in response.data

    # Check database to ensure nothing was inserted
    with app.app_context():
        assert Event.query.count() == 0
