# Copyright 2026 Google LLC
"""
Database module for the Conference Event Tracker.

This module handles connection management, table initialization,
and database CRUD operations for conference events using SQLite.
All database queries are parameterized to prevent SQL injection.
"""

import os
import sqlite3
from typing import Dict, List, Any

# Path to the SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), "events.db")


def get_db_connection() -> sqlite3.Connection:
    """
    Establish a connection to the SQLite database.

    Returns:
        sqlite3.Connection: A database connection object with row factory set.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Initialize the SQLite database schema if it doesn't already exist.
    Creates the 'events' table and seeds mock data if it is empty.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                speaker TEXT NOT NULL,
                location TEXT NOT NULL,
                category TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()

        # Check if table is empty to insert mock data
        cursor.execute("SELECT COUNT(*) FROM events")
        if cursor.fetchone()[0] == 0:
            mock_events = [
                (
                    "Keynote: NextGen Web Architectures",
                    "Sarah Chen discusses the future of edge computing, serverless architectures, and next-generation frontend systems.",
                    "Sarah Chen",
                    "Grand Ballroom A",
                    "Keynote",
                    "2026-06-04T09:00",
                    "2026-06-04T10:15",
                ),
                (
                    "Building Scalable Cloud Apps",
                    "Learn the fundamentals of designing, deploying, and maintaining high-availability microservices on Google Cloud Platform.",
                    "David Lee",
                    "Room 102",
                    "Tech Talk",
                    "2026-06-04T10:30",
                    "2026-06-04T11:30",
                ),
                (
                    "Hands-on UI Design",
                    "A practical session on building glassmorphic components, using CSS variables, and creating premium web animations from scratch.",
                    "Maria Garcia",
                    "Tech Lab B",
                    "Workshop",
                    "2026-06-04T11:45",
                    "2026-06-04T13:15",
                ),
                (
                    "Ethics in Tech Panel",
                    "Industry leaders gather to discuss the ethical implications of artificial intelligence, privacy regulations, and developer responsibilities.",
                    "Panel Speakers",
                    "Auditorium C",
                    "Panel",
                    "2026-06-04T14:00",
                    "2026-06-04T15:00",
                ),
            ]
            cursor.executemany(
                """
                INSERT INTO events (title, description, speaker, location, category, start_time, end_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                mock_events,
            )
            conn.commit()
    finally:
        conn.close()


def get_events() -> List[Dict[str, Any]]:
    """
    Retrieve all conference events from the database sorted by start time.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the events.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM events ORDER BY datetime(start_time) ASC"
        )
        rows = cursor.fetchall()
        events = [dict(row) for row in rows]
        return events
    finally:
        conn.close()


def add_event(
    title: str,
    description: str,
    speaker: str,
    location: str,
    category: str,
    start_time: str,
    end_time: str,
) -> int:
    """
    Add a new conference event to the database using parameterized queries.

    Args:
        title (str): Title of the event.
        description (str): Detailed description of the event.
        speaker (str): Speaker(s) of the event.
        location (str): Room or location of the event.
        category (str): Event category (e.g., Keynote, Workshop, etc.).
        start_time (str): Start time of the event (ISO 8601 string).
        end_time (str): End time of the event (ISO 8601 string).

    Returns:
        int: The ID of the newly inserted event row.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO events (
                title, description, speaker, location, category, start_time, end_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (title, description, speaker, location, category, start_time, end_time),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()
