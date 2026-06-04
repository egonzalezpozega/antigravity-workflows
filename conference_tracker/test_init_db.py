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

"""Unit tests for the database initialization script (init_db.py).

This module verifies that mockup event generation is correct and that the database
initialization and seeding logic is triggered correctly using mocks to prevent
side effects on any physical SQLite database.
"""

from unittest.mock import patch, MagicMock
import pytest
from database import Event
from init_db import get_mock_events, init_and_seed_db


def test_get_mock_events():
    """Verifies that get_mock_events returns 10 valid Event instances with expected attributes."""
    events = get_mock_events()
    assert isinstance(events, list)
    assert len(events) == 10
    for event in events:
        assert isinstance(event, Event)
        assert event.title
        assert event.speaker
        assert event.date
        assert event.time
        assert event.location
        assert event.category in ['Keynote', 'Workshop', 'Panel', 'Networking']
        assert event.description


@patch('init_db.Flask')
@patch('init_db.db')
@patch('init_db.Event')
def test_init_and_seed_db(mock_event_class, mock_db, mock_flask_class):
    """Verifies that init_and_seed_db correctly configures the Flask application,

    initializes the database connection, creates tables, and seeds mock events.
    """
    # Set up mock Flask app instance
    mock_app = MagicMock()
    mock_app.config = {}
    mock_flask_class.return_value = mock_app

    # Set up mock app context manager
    mock_app_context = MagicMock()
    mock_app.app_context.return_value.__enter__.return_value = mock_app_context

    # Mock the count query to return 0 (no existing data)
    mock_event_class.query.count.return_value = 0

    # Call the initialization function
    init_and_seed_db()

    # Assert Flask application was instantiated and configured
    mock_flask_class.assert_called_once_with('init_db')
    assert mock_app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///conference.db'
    assert mock_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False

    # Assert db.init_app and create_all were called
    mock_db.init_app.assert_called_once_with(mock_app)
    mock_db.create_all.assert_called_once()

    # Assert queries and additions were committed
    mock_event_class.query.count.assert_called_once()
    mock_db.session.add_all.assert_called_once()
    assert mock_db.session.commit.call_count == 1  # Committed once for addition


@patch('init_db.Flask')
@patch('init_db.db')
@patch('init_db.Event')
def test_init_and_seed_db_clears_existing_data(mock_event_class, mock_db, mock_flask_class):
    """Verifies that init_and_seed_db deletes existing events when the database is already seeded."""
    # Set up mock Flask app instance
    mock_app = MagicMock()
    mock_app.config = {}
    mock_flask_class.return_value = mock_app

    # Set up mock app context manager
    mock_app_context = MagicMock()
    mock_app.app_context.return_value.__enter__.return_value = mock_app_context

    # Mock the count query to return 5 (existing data exists)
    mock_event_class.query.count.return_value = 5

    # Call the initialization function
    init_and_seed_db()

    # Assert that delete was called on existing records
    mock_db.session.query.assert_called_with(mock_event_class)
    mock_db.session.query(mock_event_class).delete.assert_called_once()

    # Assert additions and commits happened
    mock_db.session.add_all.assert_called_once()
    assert mock_db.session.commit.call_count == 2  # Committed once for delete, once for addition
