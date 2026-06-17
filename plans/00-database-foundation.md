# 00 — Future-Proof Database Foundation
## Technical Implementation Plan — SecureCloud v3.0

**Branch:** `feature/database-foundation`  
**Must land before:** Plan 04 (Blockchain Core), Plan 05 (Event Integration), Plan 06 (Admin Dashboard)  
**Estimated effort:** 0.5 day  
**No new UI changes** — this is a pure backend/architecture refactor.

---

## Why This Plan Exists

The current `app.py` has SQLAlchemy models defined inline alongside route handlers, uses a hardcoded `SECRET_KEY`, and has no migration support. This creates three concrete problems as the project grows:

| Problem | Impact |
|---|---|
| Models in `app.py` | Every new file that needs DB access (e.g. `chain.py`) must import from `app.py`, causing **circular imports** |
| No Flask-Migrate | Adding `is_admin` to an existing `users` table on a live DB requires manually deleting the DB — **breaks any existing demo data** |
| Hardcoded `os.urandom(32)` as SECRET_KEY | Sessions are **invalidated on every restart** — logged-in users are forcibly logged out every time the server restarts |
| All config in `app.py` | Changing DB path, debug mode, or upload limits requires editing the main application file |

This plan establishes the correct layered structure **before** any blockchain code is written, so all subsequent plans build on a solid foundation.

---

## Git Workflow

> [!IMPORTANT]
> All changes happen on `feature/database-foundation`. This branch is merged to `main` **before** starting `feature/blockchain-core`. The blockchain plan's branch will be cut from the updated `main`.

### Step 1 — Create and switch to branch

```powershell
# Run from: c:\Users\Win-Rog\Documents\Secure Mini Cloud\secure-mini-cloud
git checkout -b feature/database-foundation
```

### Step 2 — Develop (all changes below)

### Step 3 — Verify all checklist items

### Step 4 — Commit (pending your approval)

```powershell
git add config.py models.py app.py requirements.txt
git commit -m "chore(db): establish future-proof database foundation

- Extract config into config.py (env-based, stable SECRET_KEY)
- Extract all SQLAlchemy models into models.py
- Add BlockchainLedger + is_admin to User model
- Add Flask-Migrate for ALTER TABLE migration support
- Add DB indexes on hot query paths
- Remove circular import risk from chain.py"
```

### Step 5 — Push (pending your approval)

```powershell
git push -u origin feature/database-foundation
```

---

## Scope of Changes

| File | Type | Summary |
|---|---|---|
| `config.py` | **NEW** | Environment-based config; stable SECRET_KEY via `.env` |
| `models.py` | **NEW** | All SQLAlchemy models: `User`, `File`, `BlockchainLedger` |
| `app.py` | **MODIFY** | Import from `config.py` and `models.py`; remove inline models/config; init Flask-Migrate |
| `requirements.txt` | **MODIFY** | Add `flask-migrate`, `python-dotenv` |
| `.env` | **NEW** | Local environment variables (gitignored) |
| `.env.example` | **NEW** | Template committed to repo — developers copy this |
| `migrations/` | **AUTO-GENERATED** | Created by `flask db init` — committed to repo |

---

## Proposed Changes

---

### `config.py` — New File

Centralises all application configuration. Uses `python-dotenv` to load a `.env` file so the `SECRET_KEY` is stable across restarts and never hardcoded in source.

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env if present; silent no-op if file is absent

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Security — loaded from .env; falls back to a random key only for CI/testing.
    # WARNING: A random fallback means sessions are lost on restart.
    # Always set SECRET_KEY in .env for any real usage.
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32)

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'secure_cloud.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload limits
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024          # 50 MB (FILE-03)
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'xlsx', 'jpg', 'png', 'zip'}
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


# Active config — override by setting APP_ENV=production in .env
config_map = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
}
active_config = config_map.get(os.environ.get('APP_ENV', 'development'), DevelopmentConfig)
```

---

### `.env` — New File (gitignored)

```ini
# .env  — LOCAL ONLY, never commit this file
SECRET_KEY=replace-this-with-a-real-64-char-random-hex-string
APP_ENV=development
# DATABASE_URL=sqlite:///instance/secure_cloud.db   # uncomment to override
```

> [!CAUTION]
> `.env` must be listed in `.gitignore`. The `SECRET_KEY` in this file is a credential — never push it to GitHub.

---

### `.env.example` — New File (committed to repo)

```ini
# .env.example — copy to .env and fill in real values
SECRET_KEY=your-secret-key-here
APP_ENV=development
```

---

### `models.py` — New File

All three SQLAlchemy models live here. This is the **single source of truth** for the database schema. `chain.py`, `app.py`, and any future module all import from here — eliminating circular imports.

```python
# models.py
# Single source of truth for all database models — SecureCloud v3.0
# Tables: users, files, blockchain_ledger

import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


# ---------------------------------------------------------------------------
# users table
# PRD v2.0 §5 + PRD v3.0 §6 (is_admin amendment)
# ---------------------------------------------------------------------------
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id             = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    username       = db.Column(db.String(150), unique=True, nullable=False)
    email          = db.Column(db.String(150), unique=True, nullable=False)
    password_hash  = db.Column(db.String(256), nullable=False)
    encryption_key = db.Column(db.String(256), nullable=False)
    is_admin       = db.Column(db.Boolean,  default=False,  nullable=False)   # PRD v3.0 §6
    created_at     = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    files = db.relationship('File', backref='owner', lazy='dynamic',
                            cascade='all, delete-orphan')

    # Index: login lookup by email is the hot path
    __table_args__ = (
        db.Index('ix_users_email',    'email'),
        db.Index('ix_users_username', 'username'),
    )

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r} is_admin={self.is_admin}>"


# ---------------------------------------------------------------------------
# files table
# PRD v2.0 §5
# ---------------------------------------------------------------------------
class File(db.Model):
    __tablename__ = 'files'

    id                = db.Column(db.String(36), primary_key=True,
                                  default=lambda: str(uuid.uuid4()))   # ISO-05: UUID, not int
    owner_id          = db.Column(db.Integer, db.ForeignKey('users.id',
                                  ondelete='CASCADE'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename   = db.Column(db.String(255), nullable=False, unique=True)
    file_size         = db.Column(db.Integer,   nullable=False)         # bytes
    uploaded_at       = db.Column(db.DateTime,  default=datetime.utcnow, nullable=False)

    # Index: dashboard query filters by owner_id
    __table_args__ = (
        db.Index('ix_files_owner_id', 'owner_id'),
    )

    def __repr__(self):
        return f"<File id={self.id!r} owner_id={self.owner_id} name={self.original_filename!r}>"


# ---------------------------------------------------------------------------
# blockchain_ledger table
# PRD v3.0 §6 + CHAIN-01
# NFR-06: Only INSERT operations are permitted on this table — never UPDATE or DELETE.
# ---------------------------------------------------------------------------
class BlockchainLedger(db.Model):
    __tablename__ = 'blockchain_ledger'

    # id auto-increments and doubles as the block index (CHAIN-01)
    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp     = db.Column(db.Text,    nullable=False)   # ISO-8601 UTC, e.g. 2025-06-13T14:32:01Z
    action        = db.Column(db.Text,    nullable=False)   # UPLOAD|DOWNLOAD|DELETE|LOGIN|LOGIN_FAIL|GENESIS
    actor         = db.Column(db.Text,    nullable=False)   # username or email-attempted
    detail        = db.Column(db.Text,    nullable=True,  default="")  # filename or IP
    previous_hash = db.Column(db.Text,    nullable=False)   # SHA-256 hex of prior block
    hash          = db.Column(db.Text,    nullable=False)   # SHA-256 hex of this block

    # Index: verify_chain() and admin ledger view both ORDER BY id ASC
    __table_args__ = (
        db.Index('ix_blockchain_ledger_id', 'id'),
    )

    def __repr__(self):
        return (f"<Block id={self.id} action={self.action!r} "
                f"actor={self.actor!r} hash={self.hash[:12]}...>")
```

---

### `app.py` — Modifications

The existing `app.py` is refactored to import its config and models instead of defining them inline. **All route logic is preserved unchanged.**

#### What changes

| Line range (current) | Change |
|---|---|
| Lines 7–26 (config + KEY + fernet) | Replace with `from config import active_config` + `app.config.from_object(...)` |
| Lines 49–65 (User + File models) | Remove — now in `models.py` |
| Lines 67–73 (user_loader + db.create_all) | Update imports; add Flask-Migrate init; add genesis seed |
| All other lines | **Unchanged** |

#### Full updated header section (lines 1–80 replacement)

```python
# app.py — SecureCloud v3.0
from flask import Flask, request, render_template, send_file, redirect, url_for, flash
import os
from cryptography.fernet import Fernet
import io
import uuid

from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate

from config import active_config
from models import db, User, File, BlockchainLedger   # single source of truth

app = Flask(__name__)
app.config.from_object(active_config)

# --- Extensions ---
db.init_app(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)       # enables: flask db init / migrate / upgrade

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- DB setup (dev convenience — production uses: flask db upgrade) ---
with app.app_context():
    db.create_all()
    # CHAIN-05: Auto-create genesis block on first run if ledger is empty
    if BlockchainLedger.query.count() == 0:
        from chain import add_block
        add_block(action="GENESIS", actor="system", detail="chain initialized")

# ... all existing route handlers follow unchanged ...
```

> [!NOTE]
> The `KEY = b'xQslvTPBF...'` hardcoded master key line in the current `app.py` is removed. The per-user Fernet key approach (already implemented) does not need a global master key — each user's `encryption_key` field is their own Fernet key stored in the DB. Removing the dead variable eliminates confusion.

---

### `requirements.txt` — Modified

Add two packages:

```diff
 blinker==1.9.0
 cffi==2.0.0
 click==8.1.8
 cryptography==46.0.3
 flask==3.1.2
+flask-migrate
+python-dotenv
 flask-sqlalchemy
 flask-bcrypt
 flask-login
 ...
```

`flask-migrate` pulls in `alembic` automatically — no additional entries needed.

---

### Migrations setup (run once after coding)

```powershell
# From project root, with venv active:
flask db init       # creates migrations/ directory (commit this)
flask db migrate -m "initial schema: users, files, blockchain_ledger"
flask db upgrade    # applies migration to instance/secure_cloud.db
```

The generated `migrations/` directory is committed to the repo. From now on, every schema change (e.g. adding a column) is handled with:

```powershell
flask db migrate -m "describe the change"
flask db upgrade
```

**No more deleting the database.**

> [!IMPORTANT]
> After running `flask db init`, add `migrations/versions/*.pyc` to `.gitignore` but **commit** the `migrations/` directory itself. The migration scripts are part of the project's source of truth.

---

### `.gitignore` additions

```gitignore
# Environment / secrets
.env

# Python cache
__pycache__/
*.pyc
*.pyo

# Database (dev instance — not for prod)
instance/secure_cloud.db

# Uploads (user data — not tracked)
uploads/
```

---

## Full Schema Summary

### `users`

| Column | Type | Constraints | Index |
|---|---|---|---|
| id | INTEGER | PK, autoincrement | — |
| username | VARCHAR(150) | UNIQUE, NOT NULL | `ix_users_username` |
| email | VARCHAR(150) | UNIQUE, NOT NULL | `ix_users_email` |
| password_hash | VARCHAR(256) | NOT NULL | — |
| encryption_key | VARCHAR(256) | NOT NULL | — |
| is_admin | BOOLEAN | NOT NULL, default False | — |
| created_at | DATETIME | NOT NULL, default utcnow | — |

### `files`

| Column | Type | Constraints | Index |
|---|---|---|---|
| id | VARCHAR(36) | PK (UUID) | — |
| owner_id | INTEGER | FK → users.id CASCADE DELETE, NOT NULL | `ix_files_owner_id` |
| original_filename | VARCHAR(255) | NOT NULL | — |
| stored_filename | VARCHAR(255) | UNIQUE, NOT NULL | — |
| file_size | INTEGER | NOT NULL | — |
| uploaded_at | DATETIME | NOT NULL, default utcnow | — |

### `blockchain_ledger`

| Column | Type | Constraints | Index |
|---|---|---|---|
| id | INTEGER | PK, autoincrement (= block index) | `ix_blockchain_ledger_id` |
| timestamp | TEXT | NOT NULL | — |
| action | TEXT | NOT NULL | — |
| actor | TEXT | NOT NULL | — |
| detail | TEXT | nullable | — |
| previous_hash | TEXT | NOT NULL | — |
| hash | TEXT | NOT NULL | — |

---

## Verification Checklist

### Structure
- [ ] `config.py` exists and `active_config` loads without error
- [ ] `models.py` exists; `db`, `User`, `File`, `BlockchainLedger` can be imported cleanly
- [ ] `app.py` imports from `config` and `models` — no inline model definitions remain
- [ ] `from chain import add_block` does NOT cause a circular import error

### Config
- [ ] `.env` is listed in `.gitignore` and not tracked by git
- [ ] `.env.example` IS tracked by git
- [ ] Restarting the Flask dev server with a `.env` SECRET_KEY does **not** invalidate the session (log in, restart, confirm still logged in)

### Migration
- [ ] `flask db init` creates `migrations/` directory
- [ ] `flask db migrate -m "initial schema"` generates a non-empty migration script
- [ ] `flask db upgrade` applies migrations without error
- [ ] `migrations/` directory is committed to the repo

### Schema
- [ ] `users` table has all 7 columns including `is_admin`
- [ ] `files` table has `ondelete='CASCADE'` on `owner_id` FK
- [ ] `blockchain_ledger` table has all 7 columns
- [ ] All indexes are present (verify with `sqlite3 instance/secure_cloud.db ".indexes"`)

### Functional regression (all v2.0 scenarios still pass)
- [ ] Register a new user → success
- [ ] Login → success, session persists across server restart (with `.env` SECRET_KEY set)
- [ ] Upload a file → encrypted blob appears in `uploads/<user_id>/`
- [ ] Download own file → original bytes received
- [ ] Attempt to download another user's file → HTTP 403
- [ ] Delete own file → blob removed from disk, row gone from `files`

### Genesis block
- [ ] Fresh DB: starting the app creates exactly 1 block with `action="GENESIS"`
- [ ] Second start: still exactly 1 block (no duplicate)

---

## Commit & Push (Requires Your Approval)

Once all checklist items are green, the following will be run — **pending your explicit approval**:

```powershell
git add config.py models.py app.py requirements.txt .env.example .gitignore migrations/
git commit -m "chore(db): establish future-proof database foundation

- Extract config into config.py (env-based, stable SECRET_KEY)
- Extract all SQLAlchemy models into models.py (User, File, BlockchainLedger)
- Add is_admin to User model; ondelete=CASCADE on files.owner_id FK
- Add DB indexes on hot query paths (email, username, owner_id, block id)
- Add Flask-Migrate (Alembic) for ALTER TABLE migration support
- Remove hardcoded KEY variable from app.py (dead code)
- Add .env / .env.example pattern; .env is gitignored"

git push -u origin feature/database-foundation
```

---

## File Tree After This Plan

```
secure-mini-cloud/
├── config.py               <- NEW  (environment-based config)
├── models.py               <- NEW  (User, File, BlockchainLedger)
├── app.py                  <- MODIFIED (imports config + models; Flask-Migrate init)
├── .env                    <- NEW, GITIGNORED (SECRET_KEY)
├── .env.example            <- NEW, COMMITTED (template)
├── migrations/             <- AUTO-GENERATED by flask db init, COMMITTED
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── <hash>_initial_schema.py
├── chain.py                <- (added in Plan 04, imports from models.py)
├── plans/
│   ├── 00-database-foundation.md   <- this file
│   └── 04-blockchain-core-module.md
├── static/style.css
├── templates/
├── instance/               <- GITIGNORED
│   └── secure_cloud.db
├── uploads/                <- GITIGNORED
├── requirements.txt        <- MODIFIED (+flask-migrate, +python-dotenv)
├── sample_data/
└── README.md
```

---

## How Subsequent Plans Build on This

| Plan | What it gains from this foundation |
|---|---|
| 04 — Blockchain Core (`chain.py`) | Imports `db`, `BlockchainLedger` from `models.py` — **zero circular import risk** |
| 05 — Event Integration | Route hooks call `add_block()` — no models changes needed |
| 06 — Admin Dashboard | `User.is_admin` already on the model; admin route queries `BlockchainLedger` via `models.py` |
| Any future feature | Add a column → `flask db migrate` + `flask db upgrade` — **no DB deletion ever needed again** |
