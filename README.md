# ✦ Antigravity Conference Tracker Workflows

Welcome to the Antigravity Conference Event Tracker repository. This repository demonstrates the power of agentic workflows in building, validating, securing, and documenting premium web applications.

## 🚀 The Upgraded Project: CosmicEvents

The core application has been upgraded from "Aura Events" to **CosmicEvents**, located in the [conference_event_tracker](file:///Users/epbgonzalez/Development/gemini-code-assist/cloud-solutions/projects/build-with-gemini-demo/build-with-antigravity/conference_event_tracker/) directory.

### Quick Links
*   **Application Source Code**: [conference_event_tracker/](file:///Users/epbgonzalez/Development/gemini-code-assist/cloud-solutions/projects/build-with-gemini-demo/build-with-antigravity/conference_event_tracker/)
*   **Documentation & Getting Started**: [conference_event_tracker/README.md](file:///Users/epbgonzalez/Development/gemini-code-assist/cloud-solutions/projects/build-with-gemini-demo/build-with-antigravity/conference_event_tracker/README.md)
*   **Main Server Entrypoint**: [conference_event_tracker/app.py](file:///Users/epbgonzalez/Development/gemini-code-assist/cloud-solutions/projects/build-with-gemini-demo/build-with-antigravity/conference_event_tracker/app.py)
*   **Automated Unit Tests**: [conference_event_tracker/test_app.py](file:///Users/epbgonzalez/Development/gemini-code-assist/cloud-solutions/projects/build-with-gemini-demo/build-with-antigravity/conference_event_tracker/test_app.py)

---

## 🔒 Hardened Security Posture
CosmicEvents was developed using strict secure-by-design guidelines, incorporating:
1.  **Anti-SQL Injection (SQLi)**: Exclusively utilizes parameterized SQLite queries.
2.  **Anti-Cross-Site Scripting (XSS)**: Default Jinja2 auto-escaping on the backend and secure `textContent` DOM manipulation on the frontend.
3.  **Cross-Site Request Forgery (CSRF) Mitigation**: Session-backed cryptographic CSRF token validation for all state-changing requests.
4.  **Security HTTP Headers**: Clickjacking (`X-Frame-Options: DENY`), MIME sniffing (`X-Content-Type-Options: nosniff`), and strict `Content-Security-Policy`.

---

## 🛠️ Local Setup
To run the server and test suite locally:
```bash
cd conference_event_tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m unittest test_app.py   # Run full test suite
python3 app.py                    # Launch server on localhost:5000
```
