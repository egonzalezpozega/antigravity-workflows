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
Unit Tests for Conference Event Tracker

Provides automated testing for app.py routes, input validation logic,
database context handling, and security mechanisms (CSRF, security headers).

Author: Antigravity AI
"""

import os
import unittest
import sqlite3
from app import app, init_db, DATABASE_PATH


class ConferenceTrackerTestCase(unittest.TestCase):

    def setUp(self):
        """Sets up a clean, isolated in-memory or temporary database for each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Set to true implicitly since we mock CSRF manually
        
        # Override Database path to a temporary file
        self.test_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_events.db')
        import app as app_module
        app_module.DATABASE_PATH = self.test_db_path
        
        # Clean up any residual test db
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            
        # Initialize schema
        init_db()
        
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Tears down the test context and removes the temporary database."""
        self.app_context.pop()
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except OSError:
                pass

    def test_database_initialization(self):
        """Verifies that the database schema is initialized and pre-populated correctly."""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]
        # Should be pre-populated with our 3 default sessions
        self.assertEqual(count, 3)
        conn.close()

    def test_dashboard_route_get(self):
        """Verifies that the dashboard landing page loads successfully with default sessions."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Convert response data to string
        html = response.data.decode('utf-8')
        
        # Verify branding elements
        self.assertIn("Cosmic", html)
        self.assertIn("Events", html)
        
        # Verify that sample events appear on the dashboard
        self.assertIn("Generative AI Frontiers in Enterprise", html)
        self.assertIn("Dr. Elena Rostova", html)
        self.assertIn("Main Auditorium (Hall A)", html)

    def test_add_event_route_get(self):
        """Verifies that the event creation page loads cleanly and generates a CSRF token."""
        response = self.client.get('/add')
        self.assertEqual(response.status_code, 200)
        
        html = response.data.decode('utf-8')
        self.assertIn("Register Conference Session", html)
        # Check if CSRF input element is generated
        self.assertIn('name="csrf_token"', html)

    def test_add_event_post_without_csrf_is_blocked(self):
        """Verifies that POSTing to event registration fails with 403 when CSRF is missing."""
        payload = {
            "title": "Quantum Cryptography Keys at Scale",
            "description": "Deploying decentralized lattices under hostile environments.",
            "speaker": "Prof. Arthur Pendelton",
            "category": "Quantum Computing",
            "event_date": "2026-07-20",
            "event_time": "10:00",
            "location": "Vanguard Stage (Hall B)"
        }
        
        response = self.client.post('/add', data=payload)
        # Should fail close with 403 Forbidden since CSRF validation is active
        self.assertEqual(response.status_code, 403)
        self.assertIn("CSRF failure", response.get_data(as_text=True))

    def test_add_event_post_with_valid_data_and_csrf_succeeds(self):
        """Verifies that event creation succeeds when complete valid inputs and CSRF are supplied."""
        # We must simulate a session with a valid csrf_token
        with self.client.session_transaction() as sess:
            sess['csrf_token'] = "test_secure_csrf_token_123"
            
        payload = {
            "csrf_token": "test_secure_csrf_token_123",
            "title": "Quantum Cryptography Keys at Scale",
            "description": "Deploying decentralized lattices under hostile environments.",
            "speaker": "Prof. Arthur Pendelton",
            "category": "Quantum Computing",
            "event_date": "2026-07-20",
            "event_time": "10:00",
            "location": "Vanguard Stage (Hall B)"
        }
        
        # Send post request
        response = self.client.post('/add', data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify that the new event got written and is rendered on the dashboard
        html = response.data.decode('utf-8')
        self.assertIn("Success! The new conference session was added securely.", html)
        self.assertIn("Quantum Cryptography Keys at Scale", html)
        self.assertIn("Prof. Arthur Pendelton", html)

    def test_add_event_post_validation_error(self):
        """Verifies that invalid or incomplete inputs trigger 400 Bad Request and display errors."""
        with self.client.session_transaction() as sess:
            sess['csrf_token'] = "test_secure_csrf_token_123"
            
        # Title too short, description too short, invalid date formatting
        payload = {
            "csrf_token": "test_secure_csrf_token_123",
            "title": "Short",
            "description": "Too brief",
            "speaker": "A",
            "category": "Quantum Computing",
            "event_date": "not-a-date",
            "event_time": "not-a-time",
            "location": "Room"
        }
        
        response = self.client.post('/add', data=payload)
        self.assertEqual(response.status_code, 400)
        
        html = response.data.decode('utf-8')
        # Check if validation helper messages are displayed
        self.assertIn("Description must be between 10 and 1000 characters.", html)
        self.assertIn("Speaker name must be between 2 and 80 characters.", html)
        self.assertIn("Invalid date format", html)

    def test_custom_error_handlers(self):
        """Verifies that requesting a non-existent URL triggers the custom 404 page."""
        response = self.client.get('/invalid-unregistered-stage-link')
        self.assertEqual(response.status_code, 404)
        
        html = response.data.decode('utf-8')
        self.assertIn("404 Not Found", html)
        self.assertIn("The requested conference page could not be located.", html)

    def test_security_headers_present(self):
        """Verifies that security response headers are present on all HTTP responses."""
        response = self.client.get('/')
        self.assertEqual(response.headers.get('X-Frame-Options'), 'DENY')
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertIsNotNone(response.headers.get('Content-Security-Policy'))


if __name__ == '__main__':
    unittest.main()
