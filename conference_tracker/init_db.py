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

"""Database initialization and seeding script.

This script creates the SQLite database tables and populates them with
realistic mockup conference events for testing and demonstration purposes.
"""

import sys
from datetime import date, time
from flask import Flask
from database import db, Event


def get_mock_events() -> list[Event]:
    """Generates a list of mockup conference events."""
    return [
        Event(
            title="Early Bird Coffee & Breakfast",
            speaker="Sponsor Showcase",
            date=date(2026, 6, 15),
            time=time(8, 0),
            location="Atrium Exhibit Hall",
            category="Networking",
            description=(
                "Kick off the conference with fresh brews and hot breakfast. Grab "
                "your badge, meet the early birds, and explore interactive sponsor booths."
            )
        ),
        Event(
            title="Opening Keynote: The Future of Agentic AI",
            speaker="Dr. Sylvia Vance",
            date=date(2026, 6, 15),
            time=time(9, 0),
            location="Grand Ballroom A",
            category="Keynote",
            description=(
                "Discover how autonomous agents and Model Context Protocol (MCP) "
                "are reshaping software engineering, workflows, and global tech "
                "industries. Gain insights into the next decade of agentic design."
            )
        ),
        Event(
            title="Hands-on Workshop: Building Secure Web Frameworks",
            speaker="Marcus Thorne",
            date=date(2026, 6, 15),
            time=time(11, 0),
            location="Workshop Hall Room 102",
            category="Workshop",
            description=(
                "A deep-dive, interactive session focusing on frontend and backend "
                "security. Learn how to prevent XSS, handle secrets, configure "
                "Content Security Policy (CSP), and secure database transactions."
            )
        ),
        Event(
            title="Panel Discussion: Human-AI Collaboration in Software",
            speaker="Elena Rostova (Mod.), Dev Patel, Chloe Vance",
            date=date(2026, 6, 15),
            time=time(14, 0),
            location="Theater Hall C",
            category="Panel",
            description=(
                "Industry experts discuss the evolving landscape of developer-agent "
                "pair programming. We'll explore ethics, productivity metrics, and "
                "the mindset shifts required to thrive as an AI-empowered developer."
            )
        ),
        Event(
            title="Interactive Laboratory: Designing Resilient Microservices",
            speaker="Sarah Jenkins",
            date=date(2026, 6, 15),
            time=time(15, 30),
            location="Workshop Hall Room 104",
            category="Workshop",
            description=(
                "Learn to build fault-tolerant microservices using circuit breakers, "
                "rate limiters, and distributed tracing. Perfect for backend architects."
            )
        ),
        Event(
            title="Networking Mixer: Beers, Bites, and Bots",
            speaker="Conference Social Committee",
            date=date(2026, 6, 15),
            time=time(17, 30),
            location="Rooftop Garden Lounge",
            category="Networking",
            description=(
                "Unwind after Day 1 with food, drinks, and lively conversations. "
                "Meet fellow attendees, share ideas, and network with sponsors and "
                "speakers in an informal, beautiful open-air setting."
            )
        ),
        Event(
            title="Deep Dive: Advanced Database Optimization and Sharding",
            speaker="Kenji Takahashi",
            date=date(2026, 6, 16),
            time=time(10, 0),
            location="Room 305 (North Wing)",
            category="Workshop",
            description=(
                "Learn state-of-the-art database architectural patterns, query optimization "
                "techniques, indexing best practices, and horizontal scaling strategies "
                "using real-world production case studies."
            )
        ),
        Event(
            title="Panel: The Future of Cloud FinOps",
            speaker="David Cho (Mod.), Linda Wu, Marcus Sterling",
            date=date(2026, 6, 16),
            time=time(11, 30),
            location="Theater Hall C",
            category="Panel",
            description=(
                "Finance meets engineering. Discover strategies for cloud cost optimization, "
                "container right-sizing, and aligning engineering velocity with financial goals."
            )
        ),
        Event(
            title="Hands-on: Mastering CSS Grid and Fluid Layouts",
            speaker="Elena Rostova",
            date=date(2026, 6, 16),
            time=time(13, 30),
            location="Design Lab Room 202",
            category="Workshop",
            description=(
                "A deep dive into advanced CSS layouts, container queries, subgrid, and "
                "modern responsive mechanics. Build complex, premium layouts with zero frameworks."
            )
        ),
        Event(
            title="Closing Session: Ethical Safeguards in Autonomous Systems",
            speaker="Aria Sterling",
            date=date(2026, 6, 16),
            time=time(15, 0),
            location="Grand Ballroom A",
            category="Keynote",
            description=(
                "As autonomous agents gain agency, establishing safety rails, alignment "
                "heuristics, and regulatory compliances is paramount. This keynote "
                "explains how to build trust into next-generation intelligent applications."
            )
        )
    ]


def init_and_seed_db():
    """Initializes the database schema and seeds it with mockup data."""
    print("Initializing Flask application context...")
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///conference.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        print("Creating database tables...")
        db.create_all()

        print("Checking if database already has data...")
        if Event.query.count() > 0:
            print("Clearing existing events to ensure a clean state...")
            db.session.query(Event).delete()
            db.session.commit()

        print("Seeding database with realistic mockup conference events...")
        mock_events = get_mock_events()
        db.session.add_all(mock_events)
        db.session.commit()

        print(f"Success! Successfully seeded {len(mock_events)} events.")


if __name__ == '__main__':
    init_and_seed_db()
