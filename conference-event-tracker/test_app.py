# Copyright 2026 Google LLC
"""
Unit tests for the Conference Event Tracker Flask Application.

This script tests the application's endpoints (GET /, GET /api/events, POST /api/events)
and verifies validation logic, database integration, and security headers.
"""

import json
import os
import unittest
from datetime import datetime, timedelta

# Override the database path to a test database file before importing app
import database
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_events.db")
database.DB_PATH = TEST_DB_PATH

from app import app


class ConferenceTrackerTestCase(unittest.TestCase):
    """Test case suite for testing Flask application endpoints."""

    def setUp(self):
        """Set up test environment: clean test database and start test client."""
        # Initialize/clear the test database
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)
        database.init_db()

        # Clear events table so test assertions can assume an empty starting slate
        conn = database.get_db_connection()
        conn.execute("DELETE FROM events")
        conn.commit()
        conn.close()

        self.app = app.test_client()
        app.config["TESTING"] = True

    def tearDown(self):
        """Tear down test environment: remove test database file."""
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except OSError:
                pass

    def test_serve_homepage(self):
        """Verify that the home page index HTML route loads successfully."""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"NextGen Schedule", response.data)
        # Check security headers
        self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertIn("Content-Security-Policy", response.headers)

    def test_get_events_empty(self):
        """Verify api/events endpoint returns empty list initially."""
        response = self.app.get("/api/events")
        self.assertEqual(response.status_code, 200)
        events = json.loads(response.data)
        self.assertEqual(len(events), 0)

    def test_add_valid_event(self):
        """Verify adding a valid event returns success and parses properly."""
        now = datetime.now()
        start = now.isoformat()[:16]  # YYYY-MM-DDTHH:MM
        end = (now + timedelta(hours=1)).isoformat()[:16]

        payload = {
            "title": "Keynote: Future of AI Coding Agents",
            "description": "An deep dive into autonomous coding tools.",
            "speaker": "Antigravity Dev Team",
            "location": "Main Hall A",
            "category": "Keynote",
            "start_time": start,
            "end_time": end
        }

        response = self.app.post(
            "/api/events",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        res_data = json.loads(response.data)
        self.assertIn("message", res_data)
        self.assertEqual(res_data["message"], "Event created successfully.")
        self.assertTrue("id" in res_data)

        # Retrieve and verify database entry
        response_get = self.app.get("/api/events")
        self.assertEqual(response_get.status_code, 200)
        events = json.loads(response_get.data)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["title"], "Keynote: Future of AI Coding Agents")
        self.assertEqual(events[0]["category"], "Keynote")
        self.assertEqual(events[0]["speaker"], "Antigravity Dev Team")

    def test_add_invalid_event_missing_fields(self):
        """Verify endpoint rejects payloads missing crucial attributes."""
        payload = {
            "title": "",
            "description": "Missing other fields",
            "speaker": "",
            "location": "Room 101",
            "category": "Workshop",
            "start_time": "2026-06-04T12:00",
            "end_time": "2026-06-04T13:00"
        }

        response = self.app.post(
            "/api/events",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        res_data = json.loads(response.data)
        self.assertIn("errors", res_data)
        self.assertGreater(len(res_data["errors"]), 0)

    def test_add_invalid_category(self):
        """Verify endpoint rejects invalid categories."""
        payload = {
            "title": "Unrecognized Category Session",
            "description": "Testing category validation logic.",
            "speaker": "Speaker A",
            "location": "Room 202",
            "category": "Networking",  # Not in Allowed Categories
            "start_time": "2026-06-04T12:00",
            "end_time": "2026-06-04T13:00"
        }

        response = self.app.post(
            "/api/events",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        res_data = json.loads(response.data)
        self.assertIn("errors", res_data)

    def test_add_invalid_time_range(self):
        """Verify endpoint rejects time ranges where end time is before start time."""
        payload = {
            "title": "Time Travelers Panel",
            "description": "Invalid time sequences.",
            "speaker": "Dr. Brown",
            "location": "Delorean Room",
            "category": "Panel",
            "start_time": "2026-06-04T15:00",
            "end_time": "2026-06-04T14:00"  # End before start
        }

        response = self.app.post(
            "/api/events",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        res_data = json.loads(response.data)
        self.assertIn("errors", res_data)
        self.assertIn("End time must be after the start time.", res_data["errors"])


if __name__ == "__main__":
    unittest.main()
