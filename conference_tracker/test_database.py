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

"""Unit tests for the database model (database.py).

This module tests the methods of the Event database model, ensuring that serialization
and string representations function correctly in an isolated environment.
"""

from datetime import date, time, datetime
import pytest
from app import app
from database import db, Event


@pytest.fixture
def db_session():
    """Sets up an isolated database session with an in-memory SQLite database."""
    from sqlalchemy import create_engine

    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

    # Create and register a safe, in-memory SQLAlchemy engine
    engine = create_engine('sqlite://')
    app.extensions['sqlalchemy']._app_engines[app] = {None: engine}

    with app.app_context():
        db.create_all()
        yield db.session
        db.session.rollback()
        db.drop_all()


def test_event_repr(db_session):
    """Verifies that the __repr__ method of the Event class returns the expected format."""
    event = Event(
        id=123,
        title="Quantum Computing Workshop",
        speaker="Dr. Alice Smith",
        date=date(2026, 6, 20),
        time=time(10, 0),
        location="Room 101",
        category="Workshop",
        description="Intro to quantum algorithms.",
        created_at=datetime(2026, 6, 4, 12, 0, 0)
    )
    assert repr(event) == "<Event 123: Quantum Computing Workshop>"


def test_event_to_dict(db_session):
    """Verifies that the to_dict serialization method correctly serializes Event attributes."""
    event = Event(
        id=456,
        title="Keynote on Ethics",
        speaker="Dr. Bob Jones",
        date=date(2026, 6, 21),
        time=time(14, 30),
        location="Grand Ballroom B",
        category="Keynote",
        description="Ethics in the age of generative models.",
        created_at=datetime(2026, 6, 4, 12, 0, 0)
    )

    expected_dict = {
        "id": 456,
        "title": "Keynote on Ethics",
        "speaker": "Dr. Bob Jones",
        "date": "2026-06-21",
        "time": "14:30",
        "location": "Grand Ballroom B",
        "category": "Keynote",
        "description": "Ethics in the age of generative models.",
        "created_at": "2026-06-04T12:00:00"
    }

    assert event.to_dict() == expected_dict


def test_event_to_dict_empty_description(db_session):
    """Verifies that to_dict handles None/empty descriptions correctly."""
    event = Event(
        id=789,
        title="Networking Hour",
        speaker="Sponsor Showcase",
        date=date(2026, 6, 21),
        time=time(17, 0),
        location="Foyer",
        category="Networking",
        description=None,
        created_at=datetime(2026, 6, 4, 12, 0, 0)
    )

    serialized = event.to_dict()
    assert serialized["description"] is None
