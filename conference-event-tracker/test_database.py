# Copyright 2026 Google LLC
"""
Unit tests for the Database module (database.py) of the Conference Event Tracker.

Tests connection acquisition, table creation, seed configuration,
and parameterized insertion/retrieval operations.
"""

import os
import sqlite3
import unittest
import database

# Override the database path to a test database file for isolated testing
TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_db_events.db")
database.DB_PATH = TEST_DB_PATH


class DatabaseTestCase(unittest.TestCase):
    """Test suite targeting the functions defined in database.py."""

    def setUp(self):
        """Set up a fresh test database for each run."""
        if os.path.exists(TEST_DB_PATH):
            os.remove(TEST_DB_PATH)

    def tearDown(self):
        """Remove the test database after each run."""
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except OSError:
                pass

    def test_get_db_connection(self):
        """Verify that get_db_connection establishes a valid connection with sqlite3.Row factory."""
        conn = database.get_db_connection()
        self.assertIsInstance(conn, sqlite3.Connection)
        self.assertEqual(conn.row_factory, sqlite3.Row)
        conn.close()

    def test_init_db_creates_table_and_seeds(self):
        """Verify init_db creates schema and seeds mock events when empty."""
        # Database file should not exist before init
        self.assertFalse(os.path.exists(TEST_DB_PATH))

        database.init_db()

        # Database file should exist now
        self.assertTrue(os.path.exists(TEST_DB_PATH))

        # Check schema and seed existence
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
        table_exists = cursor.fetchone()
        self.assertIsNotNone(table_exists)

        # Should have seeded 4 initial mock events
        cursor.execute("SELECT COUNT(*) FROM events")
        row_count = cursor.fetchone()[0]
        self.assertEqual(row_count, 4)
        conn.close()

    def test_add_event(self):
        """Verify that add_event successfully inserts a record and returns the correct lastrowid."""
        database.init_db()

        # Clear seed data for clean count assertion
        conn = database.get_db_connection()
        conn.execute("DELETE FROM events")
        conn.commit()
        conn.close()

        # Add single event
        new_id = database.add_event(
            title="Tech talk about AI",
            description="Testing database insertions.",
            speaker="Alice Developer",
            location="Room 303",
            category="Tech Talk",
            start_time="2026-06-04T13:00",
            end_time="2026-06-04T14:00"
        )
        self.assertGreater(new_id, 0)

        # Retrieve and assert details
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE id = ?", (new_id,))
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["title"], "Tech talk about AI")
        self.assertEqual(row["description"], "Testing database insertions.")
        self.assertEqual(row["speaker"], "Alice Developer")
        self.assertEqual(row["location"], "Room 303")
        self.assertEqual(row["category"], "Tech Talk")
        self.assertEqual(row["start_time"], "2026-06-04T13:00")
        self.assertEqual(row["end_time"], "2026-06-04T14:00")
        conn.close()

    def test_get_events_ordering(self):
        """Verify get_events retrieves records correctly sorted by datetime(start_time)."""
        database.init_db()

        # Clear seed data
        conn = database.get_db_connection()
        conn.execute("DELETE FROM events")
        conn.commit()
        conn.close()

        # Insert events in non-sequential order
        database.add_event("Later Event", "Desc", "Speaker", "Room A", "Tech Talk", "2026-06-04T16:00", "2026-06-04T17:00")
        database.add_event("Earlier Event", "Desc", "Speaker", "Room B", "Keynote", "2026-06-04T09:00", "2026-06-04T10:00")
        database.add_event("Middle Event", "Desc", "Speaker", "Room C", "Workshop", "2026-06-04T12:00", "2026-06-04T13:00")

        events = database.get_events()
        self.assertEqual(len(events), 3)

        # Assert ordering
        self.assertEqual(events[0]["title"], "Earlier Event")
        self.assertEqual(events[1]["title"], "Middle Event")
        self.assertEqual(events[2]["title"], "Later Event")


if __name__ == "__main__":
    unittest.main()
