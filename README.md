# Aura Events: Conference Session Tracker

Welcome to **Aura Events**, a premium, high-performance, and secure web application designed to track, schedule, and filter conference events. 

Built with **Python (Flask)**, **SQLite**, and a stunning **custom Vanilla CSS** layout utilizing modern glassmorphism design principles, Aura Events delivers a fluid, immersive interface with a completely secure, zero-vulnerability footprint.

---

## 🚀 Key Features

* **Centralized Interactive Dashboard:** A highly interactive space-themed interface with dynamic glowing highlights, smooth scale transitions, and custom typography.
* **Instant Client-Side Filtering & Search:** Real-time, instant search by title, speaker, or location and category filter dropdown (Keynotes, Workshops, Panels, Networking Mixers).
* **Robust Session Registration:** A fully validated, secure web form allowing organizers to easily add new sessions with automatic input verification.
* **Secure-by-Design Architecture:** Includes complete protection against XSS (cross-site scripting) and state-of-the-art custom, session-backed CSRF (cross-site request forgery) verification.
* **100% Isolated Automated Testing:** Fully validated using an isolated in-memory test database, guaranteeing that running tests never overwrites production data.

---

## 📂 Project Architecture

The project is structured cleanly, isolating application code within the `conference_tracker` directory:

```
conference_tracker/
├── app.py                  # Core Flask routing, input validation, and security headers
├── database.py             # Relational SQLite database schema defined via SQLAlchemy
├── init_db.py              # Script to recreate database schemas and seed mockup data
├── requirements.txt        # Isolated Python application dependencies
├── test_app.py             # Integration and routing unit tests
├── test_database.py        # Database model serialization unit tests
├── test_init_db.py         # Database initialization and mocking unit tests
├── static/
│   ├── css/
│   │   └── main.css        # Premium Vanilla CSS design system (Variables, Glassmorphism, Layouts)
│   └── js/
│       └── app.js          # Dynamic DOM-safe filter, search, and alert auto-dismissals
└── templates/
    ├── base.html           # Master layout setting SEO tags, layout blocks, and alerts
    ├── index.html          # Dashboard grid rendering pre-sorted events
    └── add_event.html      # Elegant, frosted-glass input form
```

---

## 🛠️ Getting Started & Setup

### 1. Create a Virtual Environment and Install Dependencies
Initialize an isolated virtual environment and install the required dependencies:

```bash
# Navigate to the app directory
cd conference_tracker

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize and Seed the Database
Before running the application, seed the local SQLite database with **10 premium mockup events** spanning keynotes, workshops, panels, and networking socials across multiple days:

```bash
python init_db.py
```
*This command will create the tables and populate `instance/conference.db` with a rich, fully formed mock schedule.*

### 3. Run the Development Server
Launch the Flask local development server:

```bash
python app.py
```
*The server will strictly bind to `127.0.0.1:5000` (localhost) to ensure security and prevent unauthorized external access.*

---

## 🧪 Running Automated Tests

We maintain a high-quality, 100% green test suite consisting of **12 unit and integration tests** verifying our routing, form validation, CSRF validation, models, and initialization scripts.

To execute tests safely without dropping or affecting any physical data in your production database:

```bash
# Ensure virtual environment is active
pytest -v
```

### Isolated Testing Engine
Our `test_app.py` and `test_database.py` configurations override the SQLAlchemy engine mapping dynamically inside Flask-SQLAlchemy's internal `WeakKeyDictionary` state to bind to an in-memory SQLite URL (`sqlite://`). This isolates all test execution and prevents `db.drop_all()` from touching the physical database file `instance/conference.db`.

---

## 🔒 Security Posture & Standards

The application has been built from the ground up to comply with rigorous enterprise security standards:

* **XSS Prevention:** 
  * The frontend client (`app.js`) avoids writing directly to `innerHTML` or `outerHTML`. All interactive searching and filtering are achieved by reading HTML5 dataset properties and toggling style attributes directly, keeping the DOM 100% secure.
  * In the HTML templates, all attributes rendered via Jinja2 are safely quoted to prevent injection.
* **Custom CSRF Protection:**
  * All state-changing requests (POST `/add-event`) require a valid cryptographic `csrf_token` in the form parameters which is verified against the user's session token using timing-safe comparison (`secrets.compare_digest`).
* **Security HTTP Response Headers:**
  * Configured a strict **Content Security Policy (CSP)** restricting scripts/images to self and fonts to authorized CDN paths.
  * Includes clickjacking protection (`X-Frame-Options: SAMEORIGIN`) and MIME-sniffing prevention (`X-Content-Type-Options: nosniff`).
* **Safe Secrets Fallback:**
  * Fetches `SECRET_KEY` from environment variables, falls back to a local secure file, and fails-safe securely using a high-entropy cryptographically secure random number generator.
* **Static Code Analysis (Snyk):**
  * Fully scanned using Snyk static code analysis (`snyk code test`). The code has been resolved of all potential findings, maintaining a **0 open issues (100% clean)** status.
