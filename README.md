# SecureCloud v3.0 — Blockchain Audit Ledger

A Flask-based encrypted file storage system with a **local, tamper-evident blockchain audit ledger**. Every file operation and authentication event is recorded as a cryptographically chained block. Any retrospective tampering with the audit history breaks the chain and is immediately detected.


[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red)](https://www.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Table of Contents

1. [Overview](#overview)
2. [Security Architecture](#security-architecture)
3. [Features](#features)
4. [Tech Stack](#tech-stack)
5. [Project Structure](#project-structure)
6. [Quick Start](#quick-start)
7. [Environment Configuration](#environment-configuration)
8. [Database & Migrations](#database--migrations)
9. [Blockchain Audit Ledger](#blockchain-audit-ledger)
10. [Admin Dashboard](#admin-dashboard)
11. [Demo Scenarios](#demo-scenarios)
12. [API / Route Reference](#api--route-reference)
13. [Database Schema](#database-schema)
14. [Viva Q&A Reference](#viva-qa-reference)

---

## Overview

SecureCloud delivers three compounding layers of security, each built on top of the last:

| Layer | Mechanism | What It Protects Against |
|---|---|---|
| **L1 — Encryption** | Per-user AES-128 (Fernet) key, bcrypt password hashing | Unauthorized file access; compromised storage medium |
| **L2 — Access Control** | UUID file IDs, ownership checks on every download/delete | Cross-user file access; IDOR attacks |
| **L3 — Audit Integrity** | SHA-256 hash-chained blockchain ledger | Retroactive log tampering by a rogue admin or attacker with DB access |

The full user lifecycle:

```
register → login → upload (own key, isolated storage)
         → ownership-checked download
         → blockchain event recorded
         → admin verifies chain integrity
```

---

## Security Architecture

### Per-User Encryption (L1)

- Each user is assigned a unique **Fernet key** at registration, stored in the `users` table.
- Files are **encrypted on write** and **decrypted on read** — the encrypted blob on disk (`.enc`) is binary gibberish outside the app.
- Passwords are hashed with **bcrypt** (work factor ≥ 12). No plaintext passwords are ever stored.

### Access Control (L2)

- File IDs are **UUID v4** — not sequential integers. There is no guessable pattern.
- Every `/download/<uuid>` and `/delete/<uuid>` request verifies that `file.owner_id == current_user.id`. Mismatches return **HTTP 403 Forbidden** — not a redirect, not a 404.
- Isolated upload directories: `uploads/<user_id>/` — no user can path-traverse into another user's directory.

### Blockchain Audit Ledger (L3)

A conventional SQLite audit log can be silently edited by anyone with database write access (a rogue admin, or an attacker who has achieved SQL access). The hash-chained ledger solves this:

- Each block commits to all prior blocks via `previous_hash`.
- Any modification of a past block changes its expected hash, breaking the `previous_hash` link in every subsequent block.
- `verify_chain()` detects this structurally — it is not just a policy rule.

> **Academic reference:** NIST SP 800-92 — *Guide to Computer Security Log Management* documents hash-chained audit logs as a tamper-evidence countermeasure against insider log manipulation.

---

## Features

### Authentication
- User registration with unique email + username validation
- bcrypt password hashing (work factor ≥ 12)
- Session-based login via Flask-Login
- Stable sessions across server restarts (SECRET_KEY loaded from `.env`)
- First registered account is automatically assigned **admin** privileges

### File Management
- Upload files up to **50 MB**
- Whitelisted extensions: `.txt`, `.pdf`, `.docx`, `.xlsx`, `.jpg`, `.png`, `.zip`
- AES-128 Fernet encryption applied transparently on upload
- Transparent decryption on download — user receives the original file
- Delete removes both the encrypted blob from disk and the database row
- Files tracked by UUID, not sequential IDs

### Blockchain Audit Ledger
- **Append-only** `blockchain_ledger` table — no UPDATE or DELETE ever runs on it
- Genesis block auto-created on first run
- Six auditable event types: `UPLOAD`, `DOWNLOAD`, `DELETE`, `LOGIN`, `LOGIN_FAIL`, `GENESIS`
- Each block records: index, timestamp, action, actor, detail, `previous_hash`, `hash`
- `verify_chain()` recomputes every block's hash and checks chain linkage in real time

### Admin Dashboard (`/admin`)
- Accessible only to the admin account (HTTP 403 for all others)
- Live integrity status banner: **✓ Chain Intact** or **✗ Integrity Failure — chain broken at block #N**
- Full audit ledger table: Block #, Timestamp (UTC), Action, Actor, Detail, Hash (first 12 chars)
- Tampered rows highlighted in red with a left-border accent
- No file download or user management controls — ledger view only (ADMIN-06)
- Integrity check runs server-side on **every page load** — no manual trigger

---

## Tech Stack

| Component | Technology | Notes |
|---|---|---|
| Backend | Flask 3.x (Python) | Application server |
| Database | SQLite + SQLAlchemy 2.x | ORM; three tables: `users`, `files`, `blockchain_ledger` |
| Migrations | Flask-Migrate (Alembic) | ALTER TABLE support; no DB deletion ever needed |
| Authentication | Flask-Login + Flask-Bcrypt | Session management + password hashing |
| Encryption | `cryptography` (Fernet) | AES-128 + HMAC; per-user key |
| Blockchain module | Pure Python (`hashlib`, `datetime`) | SHA-256; no external crypto library |
| Config | `python-dotenv` | Loads `.env` for stable SECRET_KEY |
| Frontend | HTML5 + Vanilla CSS | No frontend framework; custom design system in `static/style.css` |
| Fonts | Inter (Geist substitute), JetBrains Mono | Loaded from Google Fonts |

---

## Project Structure

```
secure-mini-cloud/
├── app.py                  # Flask application — routes, decorators, startup
├── chain.py                # Blockchain module — add_block(), verify_chain()
├── config.py               # Environment-based configuration (dev / prod)
├── models.py               # SQLAlchemy models — User, File, BlockchainLedger
│
├── static/
│   └── style.css           # Dark glassmorphism + admin light token system
│
├── templates/
│   ├── base.html           # Global layout, nav bar, flash messages, skip link
│   ├── index.html          # Dashboard — file list, upload form, metrics
│   ├── login.html          # Login form
│   ├── register.html       # Registration form
│   └── admin.html          # Admin dashboard — integrity banner + ledger table
│
├── migrations/             # Alembic migration scripts (committed to repo)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── plans/                  # Technical implementation plans (PRD → code)
│   ├── 00-database-foundation.md
│   ├── 04-blockchain-core-module.md
│   ├── 05-event-integration.md
│   └── 06-admin-dashboard.md
│
├── instance/
│   └── secure_cloud.db     # Auto-generated SQLite database (gitignored)
│
├── uploads/                # Isolated per-user encrypted file storage (gitignored)
│   └── <user_id>/
│       └── <uuid>.enc
│
├── sample_data/            # Sample files for testing
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template (copy to .env)
└── README.md               # This file
```

---

## Quick Start

### Prerequisites

- Python 3.9+
- Git

### 1 — Clone

```bash
git clone https://github.com/yourusername/secure-mini-cloud.git
cd secure-mini-cloud
```

### 2 — Virtual Environment

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### 4 — Configure Environment

```bash
# Copy the template
cp .env.example .env
```

Edit `.env` and set a real SECRET_KEY:

```ini
SECRET_KEY=replace-this-with-a-real-64-char-random-hex-string
APP_ENV=development
```

> **Why this matters:** Without a stable SECRET_KEY in `.env`, a new random key is generated on every restart, which invalidates all active sessions. Any user who was logged in will be silently logged out.

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5 — Apply Database Migrations

```bash
flask db upgrade
```

> On a fresh clone with no `instance/secure_cloud.db`, this creates the database and all tables. If you are running for the very first time and `migrations/` is already committed to the repo, `flask db upgrade` is all you need.

### 6 — Run

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

On first startup, the genesis block is created automatically. The first account you register will be the admin account.

---

## Environment Configuration

All configuration lives in `config.py` and is loaded from `.env` via `python-dotenv`.

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | **Yes** | Flask session signing key. Must be stable across restarts. |
| `APP_ENV` | No | `development` (default) or `production`. Controls `DEBUG` flag. |
| `DATABASE_URL` | No | SQLAlchemy connection string. Defaults to `sqlite:///instance/secure_cloud.db`. |

The `.env` file is **gitignored** — never commit it. `.env.example` is committed as a template.

---

## Database & Migrations

Schema changes are managed by **Flask-Migrate (Alembic)**. No database deletion is ever needed.

### First-time setup (already done if `migrations/` is in the repo)

```bash
flask db init          # creates migrations/ directory
flask db migrate -m "initial schema: users, files, blockchain_ledger"
flask db upgrade
```

### Adding a new column in future

```bash
flask db migrate -m "describe the change"
flask db upgrade
```

### Verify schema (SQLite CLI)

```bash
sqlite3 instance/secure_cloud.db ".schema"
sqlite3 instance/secure_cloud.db ".indexes"
```

---

## Blockchain Audit Ledger

### Architecture

The blockchain module is implemented in `chain.py` — pure Python, zero external dependencies:

```
chain.py
  ├── _compute_hash(index, timestamp, action, actor, detail, previous_hash) → str
  │     SHA-256 of all six fields in fixed order. Field order is the "protocol" —
  │     must never change once blocks exist in the DB.
  │
  ├── add_block(action, actor, detail) → None
  │     Reads last block's hash from DB → computes new hash → INSERT only.
  │     Wrapped in try/except: if DB write fails, the primary route still completes
  │     (NFR-09: graceful degradation).
  │
  └── verify_chain() → (bool, int | None)
        Fetches all blocks in ASC order.
        For each block: recomputes expected hash; checks previous_hash linkage.
        Returns (True, None) if intact; (False, N) at the first broken block.
```

### Block Structure

| Field | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment; doubles as the block index |
| `timestamp` | TEXT | ISO-8601 UTC (`2025-06-13T14:32:01Z`) |
| `action` | TEXT | `UPLOAD` · `DOWNLOAD` · `DELETE` · `LOGIN` · `LOGIN_FAIL` · `GENESIS` |
| `actor` | TEXT | Username (authenticated actions) or email attempted (`LOGIN_FAIL`) |
| `detail` | TEXT | Filename (file events) or client IP (login events) |
| `previous_hash` | TEXT | SHA-256 hex of the prior block; `"0"*64` for genesis |
| `hash` | TEXT | SHA-256 hex of this block's content |

### Genesis Block

- Created automatically on first run if `blockchain_ledger` is empty.
- `action = "GENESIS"`, `actor = "system"`, `previous_hash = "0" * 64`.
- Starting the app a second time does **not** create a duplicate.

### Hash Formula

```
hash = SHA-256(str(index) + timestamp + action + actor + detail + previous_hash)
```

The field concatenation order is fixed — this is the chain's "protocol". Changing it retroactively would invalidate all existing blocks.

### Audited Events

| Route | Trigger | action | actor | detail |
|---|---|---|---|---|
| `POST /` | File encrypted + committed to DB | `UPLOAD` | `current_user.username` | original filename |
| `GET /download/<uuid>` | File decrypted + streamed | `DOWNLOAD` | `current_user.username` | original filename |
| `POST /delete/<uuid>` | File removed from disk + DB | `DELETE` | `current_user.username` | original filename |
| `POST /login` (success) | `login_user()` called | `LOGIN` | `user.username` | client IP |
| `POST /login` (failure) | Credentials rejected | `LOGIN_FAIL` | email attempted | client IP |

`add_block()` is always called **after** the primary operation succeeds. A failed upload, failed decryption, or failed DB write does not produce a false audit entry (AUDIT-06).

### Tamper Detection

The `verify_chain()` function provides a structural guarantee:

1. Fetches all blocks ordered by `id ASC`.
2. For each block `i`:
   - Recomputes `_compute_hash(block.id, block.timestamp, ...)` from stored fields.
   - Compares recomputed hash to `block.hash`. Mismatch → `(False, block.id)`.
   - If `i > 0`: checks `block.previous_hash == blocks[i-1].hash`. Mismatch → `(False, block.id)`.
3. Returns `(True, None)` if all blocks pass.

This runs on **every page load** of `/admin` — no manual trigger needed.

### Smoke Test (PowerShell)

```powershell
python -c "
from app import app
from models import BlockchainLedger
from chain import verify_chain
with app.app_context():
    blocks = BlockchainLedger.query.order_by(BlockchainLedger.id.asc()).all()
    print(f'Total blocks: {len(blocks)}')
    for b in blocks:
        print(f'  Block #{b.id}: {b.action:12s} actor={b.actor!r:20s} detail={b.detail!r}')
    ok, broken_at = verify_chain()
    print(f'Chain intact: {ok} | Broken at: {broken_at}')
"
```

---

## Admin Dashboard

### Access

- URL: `/admin`
- Only the **first registered account** has `is_admin = True`. All subsequent accounts are regular users.
- Non-admin authenticated users → **HTTP 403 Forbidden**
- Unauthenticated users → redirect to `/login`
- The admin nav button (🛡 Admin) is only visible in the nav bar for admin users.

### What It Shows

- **Integrity Status Banner** (top of page, auto-refreshes on every load):
  - 🟢 `✓ Chain Intact — all N blocks verified`
  - 🔴 `✗ Integrity Failure — chain broken at block #N`
- **Full Audit Ledger Table** (newest blocks first):
  - Block #, Timestamp (UTC), Action badge, Actor, Detail, Hash (first 12 chars + `…`)
  - Tampered rows are highlighted in red with a left-border accent
- **No file download or user management controls** — this page is a read-only audit view (ADMIN-06).

### Admin Account Setup

The admin account is determined **purely by registration order** — no manual seeding required:

1. Start the app on a fresh database.
2. Register the first account → this account automatically gets `is_admin = True`.
3. All subsequent accounts get `is_admin = False`.

If you reset the database (delete `instance/secure_cloud.db`), the first registration on the new DB becomes the new admin.


---

## API / Route Reference

| Method | Route | Auth | Description |
|---|---|---|---|
| `GET` | `/` | Login required | Dashboard — list user's files |
| `POST` | `/` | Login required | Upload a file (encrypt + store + `add_block(UPLOAD)`) |
| `GET` | `/download/<uuid>` | Login required | Download + decrypt file; ownership enforced; `add_block(DOWNLOAD)` |
| `POST` | `/delete/<uuid>` | Login required | Delete file from disk + DB; ownership enforced; `add_block(DELETE)` |
| `GET` | `/register` | Public | Registration form |
| `POST` | `/register` | Public | Create account; first account gets `is_admin=True` |
| `GET` | `/login` | Public | Login form |
| `POST` | `/login` | Public | Authenticate; `add_block(LOGIN or LOGIN_FAIL)` |
| `GET` | `/logout` | Login required | Destroy session |
| `GET` | `/admin` | Admin required | Blockchain ledger + integrity banner (HTTP 403 for non-admins) |

---

## Database Schema

### `users`

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PK, autoincrement |
| username | VARCHAR(150) | UNIQUE, NOT NULL |
| email | VARCHAR(150) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(256) | NOT NULL |
| encryption_key | VARCHAR(256) | NOT NULL (per-user Fernet key) |
| is_admin | BOOLEAN | NOT NULL, default False |
| created_at | DATETIME | NOT NULL, default utcnow |

### `files`

| Column | Type | Constraints |
|---|---|---|
| id | VARCHAR(36) | PK (UUID v4) |
| owner_id | INTEGER | FK → users.id ON DELETE CASCADE, NOT NULL |
| original_filename | VARCHAR(255) | NOT NULL |
| stored_filename | VARCHAR(255) | UNIQUE, NOT NULL |
| file_size | INTEGER | NOT NULL (bytes) |
| uploaded_at | DATETIME | NOT NULL, default utcnow |

### `blockchain_ledger`

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PK, autoincrement (= block index) |
| timestamp | TEXT | NOT NULL (ISO-8601 UTC) |
| action | TEXT | NOT NULL (`UPLOAD` · `DOWNLOAD` · `DELETE` · `LOGIN` · `LOGIN_FAIL` · `GENESIS`) |
| actor | TEXT | NOT NULL |
| detail | TEXT | nullable |
| previous_hash | TEXT | NOT NULL (SHA-256 hex) |
| hash | TEXT | NOT NULL (SHA-256 hex) |



---