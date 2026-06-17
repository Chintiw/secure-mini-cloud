# 4.1 Blockchain Core Module (CHAIN)
## Technical Implementation Plan — SecureCloud v3.0

**Source PRD:** `SecureCloud_PRD_v3_Blockchain.md` · Section 4.1 (Requirements CHAIN-01 through CHAIN-05)  
**Builds on:** v2.0 Level-Up MVP (authentication, per-user Fernet encryption, SQLite + SQLAlchemy — all complete)  
**Estimated effort:** 1 day (M1 from PRD milestone table)  
**Branch:** `feature/blockchain-core`

---

## Background

The v2.0 MVP stores files encrypted per-user but has **no audit trail**. Any row in a plain SQLite table can be silently edited or deleted — this is documented as a critical weakness in NIST SP 800-92.

This module adds a **local, append-only, SHA-256 hash-chained ledger** stored in a new `blockchain_ledger` SQLite table. Every block cryptographically commits to all prior blocks; modifying any past block breaks the chain and is immediately detectable via `verify_chain()`.

This plan covers **only the CHAIN module** (Section 4.1). The event hooks (AUDIT, Section 4.2) and admin dashboard (ADMIN, Section 4.3) are separate plans.

---

## Git Workflow

> [!IMPORTANT]
> All changes are made on the feature branch — **never directly on `main`**. When all spec items are verified, you will be asked to approve the commit and push.

### Step 1 — Create and switch to the feature branch

```powershell
# Run from: c:\Users\Win-Rog\Documents\Secure Mini Cloud\secure-mini-cloud
git checkout -b feature/blockchain-core
```

Expected output: `Switched to a new branch 'feature/blockchain-core'`

### Step 2 — Develop (all changes described below)

### Step 3 — Verify all spec items (checklist at end of plan)

### Step 4 — Commit (pending your approval)

```powershell
git add chain.py app.py
git commit -m "feat(chain): add blockchain core module (CHAIN-01 to CHAIN-05)

- Add chain.py with Block dataclass, _compute_hash(), add_block(), verify_chain()
- Add BlockchainLedger SQLAlchemy model to app.py
- Add is_admin column to User model
- Genesis block auto-created on first run if ledger is empty"
```

### Step 5 — Push (pending your approval)

```powershell
git push -u origin feature/blockchain-core
```

---

## Scope of Changes

This plan touches exactly **2 files**:

| File | Change Type | Why |
|---|---|---|
| `chain.py` | **NEW** | The entire blockchain module (CHAIN-01 to CHAIN-05) |
| `app.py` | **MODIFY** | Add `BlockchainLedger` model + `is_admin` column to `User` model |

> [!NOTE]
> `requirements.txt` is **not changed** — `hashlib` and `datetime` are Python stdlib. SQLAlchemy is already installed.

---

## Proposed Changes

---

### `chain.py` — New File

**Full path:** `secure-mini-cloud/chain.py`

This is the standalone blockchain module. It imports only from `hashlib`, `datetime`, and the SQLAlchemy models in `app.py`. It exposes two public functions and one internal helper.

#### Internal details

**`_compute_hash(index, timestamp, action, actor, detail, previous_hash) → str`**

Satisfies **CHAIN-02**.

- Concatenates all six fields as a single UTF-8 string in a deterministic order.
- Returns the lowercase hex digest of `hashlib.sha256(raw.encode()).hexdigest()`.
- No external crypto library — stdlib only (NFR-07).
- The field order is fixed: `index → timestamp → action → actor → detail → previous_hash`. This order must never change once blocks exist in the DB — it is the "protocol".

**`add_block(action: str, actor: str, detail: str = "") → None`**

Satisfies **CHAIN-03** and **CHAIN-05**.

1. Queries `BlockchainLedger` for the row with the highest `id` (last block).
2. If no rows exist → this is the first call; `prev_hash = "0" * 64`, `index = 1` (genesis will be `id=1`).
3. If rows exist → `prev_hash = last.hash`, `index = last.id + 1`.
4. Computes the new block's hash via `_compute_hash`.
5. Creates a `BlockchainLedger` instance and calls `db.session.add()` + `db.session.commit()`.
6. Wrapped in a `try/except Exception` — if the DB write fails, the exception is logged server-side but **not re-raised** (NFR-09: graceful degradation — the calling route's primary operation must still complete).

> [!IMPORTANT]
> `add_block` must be called **inside an active Flask application context** (i.e., from within a route handler or `with app.app_context()`). It must never be called at module import time.

**`verify_chain() → tuple[bool, int | None]`**

Satisfies **CHAIN-04**.

1. Fetches all rows from `blockchain_ledger` ordered by `id ASC`.
2. For each block `i`:
   - Recomputes its expected hash from its stored fields using `_compute_hash`.
   - Compares recomputed hash to stored `block.hash`. Mismatch → return `(False, block.id)`.
   - If `i > 0`: checks `block.previous_hash == blocks[i-1].hash`. Mismatch → return `(False, block.id)`.
3. Returns `(True, None)` if all blocks pass.

**Genesis block auto-creation (CHAIN-05)**

The genesis block is created by calling `add_block(action="GENESIS", actor="system", detail="chain initialized")` **once**, inside `with app.app_context()` after `db.create_all()` runs — but only if `BlockchainLedger.query.count() == 0`.

This is placed inside `app.py`'s DB setup block (see below), not in `chain.py` itself, to avoid circular imports.

#### Full implementation

```python
# chain.py
# Blockchain Core Module — SecureCloud v3.0
# Satisfies: CHAIN-01, CHAIN-02, CHAIN-03, CHAIN-04
# CHAIN-05 (genesis) is triggered from app.py after db.create_all()

import hashlib
import datetime
import logging

logger = logging.getLogger(__name__)


def _compute_hash(index: int, timestamp: str, action: str,
                  actor: str, detail: str, previous_hash: str) -> str:
    """
    CHAIN-02: SHA-256 of all six block fields concatenated in fixed order.
    Field order: index | timestamp | action | actor | detail | previous_hash
    This order is the chain's 'protocol' — must never change once blocks exist.
    """
    raw = f"{index}{timestamp}{action}{actor}{detail}{previous_hash}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def add_block(action: str, actor: str, detail: str = "") -> None:
    """
    CHAIN-03: Append a new block to the chain.
    Reads the last block's hash from the DB to form the cryptographic link.
    NFR-09: Exceptions are caught and logged — primary route operations are unaffected.
    """
    # Import inside function to avoid circular import at module load time
    from app import db, BlockchainLedger

    try:
        last = BlockchainLedger.query.order_by(BlockchainLedger.id.desc()).first()

        if last is None:
            # No blocks yet — this becomes block #1
            prev_hash = "0" * 64
            new_index = 1
        else:
            prev_hash = last.hash
            new_index = last.id + 1

        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        block_hash = _compute_hash(
            index=new_index,
            timestamp=timestamp,
            action=action,
            actor=actor,
            detail=detail,
            previous_hash=prev_hash,
        )

        entry = BlockchainLedger(
            timestamp=timestamp,
            action=action,
            actor=actor,
            detail=detail,
            previous_hash=prev_hash,
            hash=block_hash,
        )
        db.session.add(entry)
        db.session.commit()

    except Exception as exc:  # NFR-09: graceful degradation
        logger.error("add_block failed (action=%s, actor=%s): %s", action, actor, exc)


def verify_chain() -> tuple:
    """
    CHAIN-04: Verify the entire chain's integrity.
    Returns (True, None) if intact.
    Returns (False, block_id) at the first broken link.
    """
    from app import BlockchainLedger

    blocks = BlockchainLedger.query.order_by(BlockchainLedger.id.asc()).all()

    for i, block in enumerate(blocks):
        # Step 1: Recompute this block's hash from its stored fields
        recomputed = _compute_hash(
            index=block.id,
            timestamp=block.timestamp,
            action=block.action,
            actor=block.actor,
            detail=block.detail,
            previous_hash=block.previous_hash,
        )
        if recomputed != block.hash:
            return False, block.id

        # Step 2: Check that this block correctly references the previous block
        if i > 0 and block.previous_hash != blocks[i - 1].hash:
            return False, block.id

    return True, None
```

---

### `app.py` — Modifications

**Full path:** `secure-mini-cloud/app.py`

Three targeted changes to the existing file. No existing logic is removed or altered.

#### Change A — Add `BlockchainLedger` SQLAlchemy model

Insert after the existing `File` model class (currently at line 58–65). This satisfies the database design in PRD Section 6.

```python
class BlockchainLedger(db.Model):
    __tablename__ = 'blockchain_ledger'
    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp     = db.Column(db.Text, nullable=False)
    action        = db.Column(db.Text, nullable=False)   # UPLOAD|DOWNLOAD|DELETE|LOGIN|LOGIN_FAIL|GENESIS
    actor         = db.Column(db.Text, nullable=False)
    detail        = db.Column(db.Text, nullable=True, default="")
    previous_hash = db.Column(db.Text, nullable=False)
    hash          = db.Column(db.Text, nullable=False)

    # NFR-06: This model must NEVER be used with db.session.delete() or UPDATE queries.
    # Only db.session.add() (INSERT) is permitted — enforced by convention.
```

#### Change B — Add `is_admin` column to `User` model

Amend the existing `User` model to include the `is_admin` flag (PRD Section 6, "Amendment to users table"). This is required by the admin dashboard work (Section 4.3) but the column is added now so the DB schema is consistent.

```python
# Add inside the User class, after existing columns:
is_admin = db.Column(db.Boolean, default=False, nullable=False)
```

#### Change C — Seed genesis block after `db.create_all()`

Replace the existing DB setup block:

```python
# BEFORE (current app.py lines 72-73):
with app.app_context():
    db.create_all()
```

```python
# AFTER:
with app.app_context():
    db.create_all()
    # CHAIN-05: Auto-create genesis block on first run if ledger is empty
    from chain import add_block
    if BlockchainLedger.query.count() == 0:
        add_block(action="GENESIS", actor="system", detail="chain initialized")
```

> [!WARNING]
> The genesis seed runs every time the app starts, but only inserts if `count() == 0`. This is safe but means it runs one DB query on every startup — negligible at this scale.

---

## Database Impact

After these changes, `db.create_all()` will create the `blockchain_ledger` table and add the `is_admin` column to `users` if they don't already exist.

> [!CAUTION]
> **Existing database:** If `instance/secure_cloud.db` already exists from v2.0, SQLAlchemy's `create_all()` will add the new `blockchain_ledger` table automatically. However, it will **NOT** add the `is_admin` column to an existing `users` table — SQLAlchemy does not do ALTER TABLE migrations.
>
> **Fix for dev:** Delete `instance/secure_cloud.db` and restart the app to get a fresh schema. This is fine for the demo environment.

---

## Verification Checklist

Work through this checklist on the `feature/blockchain-core` branch before approving the commit.

### CHAIN-01 — Block data structure
- [ ] `BlockchainLedger` model has all seven fields: `id`, `timestamp`, `action`, `actor`, `detail`, `previous_hash`, `hash`
- [ ] All fields match PRD Section 6 column types

### CHAIN-02 — Hash computation
- [ ] `_compute_hash` uses `hashlib.sha256` (no external library)
- [ ] All six fields are included in the hash input in the specified order
- [ ] Same inputs always produce the same hash (deterministic)

### CHAIN-03 — `add_block()` function
- [ ] Reads the last block's hash from DB before inserting
- [ ] Sets `previous_hash = "0" * 64` when ledger is empty
- [ ] Calls only `db.session.add()` — never `UPDATE` or `DELETE`
- [ ] Exceptions are caught and logged, not re-raised (NFR-09)

### CHAIN-04 — `verify_chain()` function
- [ ] Fetches all blocks ordered by `id ASC`
- [ ] Recomputes each block's hash and compares to stored hash
- [ ] Checks `block[n].previous_hash == block[n-1].hash` for all n > 0
- [ ] Returns `(True, None)` when chain is intact
- [ ] Returns `(False, N)` where N is the first broken block's id

### CHAIN-05 — Genesis block auto-creation
- [ ] Starting the app with an empty DB creates exactly one genesis block
- [ ] Genesis block has `action="GENESIS"`, `actor="system"`, `previous_hash="0"*64`
- [ ] Starting the app a second time does NOT create a duplicate genesis block

### NFR checks
- [ ] NFR-06: No `UPDATE` or `DELETE` calls in `chain.py` or the new model
- [ ] NFR-07: Only `hashlib` used — no `cryptography`, no external package
- [ ] NFR-08: No network calls anywhere in `chain.py`
- [ ] NFR-09: Calling `add_block` when DB is unavailable does not crash the app

### Tamper detection smoke test (PRD Demo Scenario 5)
1. Start the app fresh (delete `instance/secure_cloud.db` first)
2. Register a user — this triggers a `LOGIN` block
3. Open `instance/secure_cloud.db` in DB Browser for SQLite
4. Edit the `detail` field of block #1 to any different value
5. Call `verify_chain()` from a Python shell inside the app context
6. Confirm it returns `(False, 1)`

```powershell
# Quick smoke test from project root (PowerShell)
python -c "
from app import app, db, BlockchainLedger
from chain import verify_chain, add_block
with app.app_context():
    print('Block count:', BlockchainLedger.query.count())
    ok, broken_at = verify_chain()
    print('Chain intact:', ok, '| Broken at:', broken_at)
"
```

---

## Commit & Push (Requires Your Approval)

Once all checklist items above are verified, the following will be run — **pending your explicit approval**:

```powershell
# Stage only the two changed files
git add chain.py app.py

# Commit with a descriptive message
git commit -m "feat(chain): add blockchain core module (CHAIN-01 to CHAIN-05)

- Add chain.py: _compute_hash(), add_block(), verify_chain()
- Add BlockchainLedger SQLAlchemy model (blockchain_ledger table)
- Add is_admin column to User model
- Seed genesis block on first run (CHAIN-05)
- NFR-09: add_block() failures are logged, never propagated"

# Push the feature branch to origin
git push -u origin feature/blockchain-core
```

After the push, a Pull Request can be opened from `feature/blockchain-core` → `main` for final review.

---

## File Tree After This Plan

```
secure-mini-cloud/
├── chain.py                        <- NEW  (CHAIN-01 to CHAIN-05)
├── app.py                          <- MODIFIED (BlockchainLedger model, is_admin, genesis seed)
├── plans/
│   └── 04-blockchain-core-module.md
├── static/style.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   └── register.html
├── instance/secure_cloud.db
├── uploads/
├── requirements.txt                <- UNCHANGED (no new dependencies)
└── README.md
```

---

## What This Plan Does NOT Cover

These are handled in separate plans:

| Section | Plan |
|---|---|
| 4.2 Event Integration (AUDIT-01 to AUDIT-06) | `05-event-integration.md` |
| 4.3 Admin Dashboard (ADMIN-01 to ADMIN-06) | `06-admin-dashboard.md` |
| README.md blockchain section update | Included in `06-admin-dashboard.md` |
