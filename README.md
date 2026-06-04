# NextGen Schedule - Conference Event Tracker

NextGen Schedule is a premium, interactive Single-Page Application (SPA) designed to discover, track, search, filter, and create upcoming conference events. The system is built with a lightweight Python/Flask backend and a secure SQLite database, styled with a high-end glassmorphic dark-theme user interface.

## Features

- **Dynamic Interactive Dashboard**: Modern dark-mode interface with a glowing glassmorphism aesthetic, smooth micro-animations, and responsive grids.
- **Real-Time Search & Filtering**: Instant search across titles, descriptions, speakers, and rooms, alongside category filtering pills (Keynotes, Workshops, Panels, Tech Talks).
- **Personalized Scheduling**: Star favorite events to dynamically persist them in a custom "My Schedule" track using `localStorage`.
- **Dynamic Stats Dashboard**: Real-time summary counts of total events, keynotes, workshops, and starred items currently in your schedule.
- **Robust Security**: Multi-layered defense design incorporating parameterized SQL queries, Strict Content Security Policies (CSP), and client-side XSS safeguards.

---

## Tech Stack

- **Backend**: Python 3.11+, Flask, Loguru (premium structured logging).
- **Database**: SQLite3.
- **Frontend**: Semantic HTML5, CSS3 (Vanilla Custom Properties, Flexbox/Grid layouts), Vanilla JavaScript (state management, safe DOM rendering).
- **Testing**: Python standard library `unittest` module.

---

## Project Structure

```text
conference-event-tracker/
├── app.py             # Flask web server, API routing, & security headers
├── database.py        # SQLite connection handling, parameterized schema, and seeding
├── test_app.py        # API routing and payload validation tests
├── test_database.py   # Database connections and CRUD parameter tests
├── templates/
│   └── index.html     # Semantic single-page structure and SEO meta tags
└── static/
    ├── css/
    │   └── style.css  # CSS variables, glassmorphic styles, responsive grid, animations
    └── js/
        └── app.js     # State manager, event handers, and secure DOM builders
```

---

## Getting Started

### Prerequisites

Ensure you have Python 3.11+ installed on your system.

### Installation & Run

1. **Navigate to the application folder**:
   ```bash
   cd conference-event-tracker
   ```

2. **Set up a Python virtual environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install flask loguru
   ```

5. **Start the application server**:
   ```bash
   python app.py
   ```

6. **Access the application**:
   Open your browser and navigate to: `http://127.0.0.1:5000`
   *Note: Upon startup, the database `events.db` will automatically initialize and seed with pre-populated mock events (Keynotes, Tech Talks, Workshops, and Panels) to showcase the interface.*

---

## Verification & Testing

The application includes a complete suite of unit tests validating the Flask routes, database integration, payload validation, and sorting order.

To run the automated test suite locally:

```bash
cd conference-event-tracker
source venv/bin/activate
python -m unittest discover -s .
```

---

## Security Defenses

- **SQL Injection Prevention**: Database operations use strictly parameterized SQL bindings (`?` placeholders) inside the `database.py` module.
- **Cross-Site Scripting (XSS) Mitigation**: The frontend exclusively constructs HTML using safe DOM manipulation standard APIs like `textContent` and `createElement` in `app.js`. Direct `innerHTML` assignments are avoided.
- **Strict HTTP Headers**: Expressed via Flask middleware to ensure every response has:
  - `Content-Security-Policy`: Restricts scripts and defaults to `'self'` to block unauthorized cross-site scripts.
  - `X-Frame-Options: DENY`: Prevents clickjacking attacks.
  - `X-Content-Type-Options: nosniff`: Guards against MIME sniffing.
  - `Referrer-Policy: strict-origin-when-cross-origin`: Minimizes referrer leaks.
- **Production Safety**: Flask runs bound strictly to localhost (`127.0.0.1`) and loads its debugging flag via `FLASK_DEBUG` from the environment, defaulting securely to `False` in development or production settings.
