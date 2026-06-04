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

"""Database configuration and models for the Conference Event Tracker.

This module sets up the SQLAlchemy database object and defines the
Event data model for storing conference session information.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy object without binding it to a specific app.
# The app will bind to it dynamically using db.init_app(app).
db = SQLAlchemy()


class Event(db.Model):
    """Data model representing a conference event/session.

    Attributes:
        id: Unique identifier for each event (Primary Key).
        title: Title of the conference session.
        speaker: Name of the presenter or organizer.
        date: Date of the event.
        time: Starting time of the event.
        location: Room, venue, or virtual meeting URL.
        category: Session type (e.g., Keynote, Workshop, Panel).
        description: Brief summary or description of the session.
        created_at: Timestamp of when the record was created.
    """

    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    speaker = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        """Returns a string representation of the Event instance."""
        return f"<Event {self.id}: {self.title}>"

    def to_dict(self) -> dict:
        """Serializes the Event model instance to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "speaker": self.speaker,
            "date": self.date.isoformat(),
            "time": self.time.strftime("%H:%M"),
            "location": self.location,
            "category": self.category,
            "description": self.description,
            "created_at": self.created_at.isoformat()
        }
