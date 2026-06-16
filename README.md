# SecureCloud Level-Up MVP

A robust, secure, and modern Flask-based web application for demonstrating per-user encryption, secure file uploads, and cryptographic data isolation. This project has evolved from a basic MVP into a full-featured "cyber security" product.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/) [![Flask](https://img.shields.io/badge/Flask-3.0%2B-green)](https://flask.palletsprojects.com/) [![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red)](https://www.sqlalchemy.org/)

## Features

- **User Authentication**: Secure registration and login using `flask-login` and bcrypt password hashing (work factor >= 12).
- **Per-User Encryption**: Every user gets a unique, automatically generated AES-based Fernet encryption key upon registration.
- **Data Isolation**: Uploads are stored in isolated user directories (`uploads/<user_id>`), encrypted on-the-fly.
- **Strict Access Control**: Files are tracked via unguessable UUIDs in the database. Download routes verify ownership; mismatched attempts are blocked with HTTP 403 Forbidden.
- **File Operations**: 
  - Upload files up to 50 MB.
  - Whitelisted extensions (`.txt`, `.pdf`, `.docx`, `.xlsx`, `.jpg`, `.png`, `.zip`).
  - Delete files (removes the encrypted blob from disk and the database record).
- **Premium UI/UX**: Completely styled with a modern "dark mode" design system, featuring glassmorphism, responsive data tables, metric cards, and CSS animations.

## Tech Stack
- **Backend**: Flask (Python web framework)
- **Database**: SQLite + SQLAlchemy (ORM)
- **Authentication**: Flask-Login + Flask-Bcrypt
- **Encryption**: `cryptography` library (Fernet for AES-128 + HMAC)
- **Frontend**: HTML5 + Vanilla CSS (Custom styling in `static/style.css`)
- **Storage**: Local filesystem (`instance/secure_cloud.db`, `uploads/` dir)

## Quick Start

### Prerequisites
- Python 3.9+ installed
- Git (for cloning)

### Installation
1. **Clone the Repo**:
   ```bash
   git clone https://github.com/yourusername/secure-mini-cloud.git
   cd secure-mini-cloud
   ```

2. **Set Up Virtual Environment** (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Mac/Linux
   # or `.venv\Scripts\activate` on Windows
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the App**:
   ```bash
   python app.py
   ```
   - The database (`instance/secure_cloud.db`) is generated automatically upon the first run.
   - Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Usage Guide (Demo Scenarios)

1. **Register & Login**:
   - Create an account at `/register`. Log in at `/login`.
2. **Upload & Encryption Verification**:
   - Upload a test file on the dashboard.
   - Navigate to `uploads/<your_user_id>/` in your file explorer. Open the `.enc` file in a text editor to verify it is unreadable binary gibberish.
3. **Cross-User Access Blocked**:
   - Right-click "Download" on your file and copy the link.
   - Log out, register a second account, and paste the link.
   - The server will return a `403 Forbidden` error.
4. **Delete Verification**:
   - Click "Delete" on the dashboard. The file vanishes from the UI, the `.enc` file is removed from disk, and the database record is dropped.

## Project Structure
```
secure-mini-cloud/
├── app.py                 # Flask backend (routes, models, encryption logic)
├── static/
│   └── style.css          # Premium dark mode design system
├── templates/
│   ├── base.html          # Global layout & flash messages
│   ├── index.html         # Dashboard & upload metrics
│   ├── login.html         # Login form
│   └── register.html      # Registration form
├── instance/
│   └── secure_cloud.db    # Auto-generated SQLite database
├── uploads/               # Isolated user directories containing .enc files
├── sample_data/           # Sample files for testing
├── requirements.txt       # Python dependencies
└── README.md              # This documentation
```
