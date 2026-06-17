# 4.2 Event Integration (AUDIT)
## Technical Implementation Plan — SecureCloud v3.0

**Source PRD:** `SecureCloud_PRD_v3_Blockchain.md` · Section 4.2 (Requirements AUDIT-01 through AUDIT-06)  
**Depends on:** Plan 00 (Database Foundation — complete), Plan 04 (Blockchain Core — complete)  
**Estimated effort:** 0.5 day (M3 from PRD milestone table)  
**Branch:** `feature/event-integration`

---

## Background

Plan 04 delivered `chain.py` with `add_block()` and `verify_chain()`, plus the `BlockchainLedger` model and genesis block seeding. The chain infrastructure is in place — **but no application events are recorded yet.**

This plan wires `add_block()` calls into the existing route handlers in `app.py` so that every auditable event (upload, download, delete, login success, login failure) is captured as a cryptographically-linked block in the blockchain ledger.

After this plan, the full audit trail will be functional:
- **UPLOAD** — recorded when a file is successfully encrypted and stored
- **DOWNLOAD** — recorded when a file is successfully decrypted and served
- **DELETE** — recorded when a file is successfully removed from disk and DB
- **LOGIN** — recorded on successful authentication
- **LOGIN_FAIL** — recorded on failed authentication (with email attempted and IP)

---

## Git Workflow

> [!IMPORTANT]
> All changes are made on the feature branch `feature/event-integration` — **never directly on `main`**. The branch is merged to `main` only after all spec items are verified and you explicitly approve.

### Step 1 — Create and switch to the feature branch

```powershell
# Run from: c:\Users\Win-Rog\Documents\Secure Mini Cloud\secure-mini-cloud
git checkout -b feature/event-integration
```

Expected output: `Switched to a new branch 'feature/event-integration'`

### Step 2 — Develop (all changes described below)

### Step 3 — Verify all spec items (checklist at the end of this plan)

### Step 4 — Commit (pending your approval)

```powershell
git add app.py
git commit -m "feat(audit): wire add_block() into all route handlers (AUDIT-01 to AUDIT-06)

- AUDIT-01: UPLOAD event after successful encrypt + DB write
- AUDIT-02: DOWNLOAD event after successful decrypt + stream
- AUDIT-03: DELETE event after successful disk + DB removal
- AUDIT-04: LOGIN_FAIL event with email + IP on bad credentials
- AUDIT-05: LOGIN event with username + IP on successful auth
- AUDIT-06: All add_block() calls placed after primary operation succeeds
- NFR-09: add_block failures are caught inside chain.py, never propagated"
```

### Step 5 — Push (pending your approval)

```powershell
git push -u origin feature/event-integration
```

### Step 6 — Merge to main (pending your approval)

After all verification passes and you give the green light:

```powershell
# Switch to main
git checkout main

# Merge the feature branch (fast-forward if possible)
git merge feature/event-integration

# Push updated main to origin
git push origin main
```

### Step 7 — Prune the feature branch permanently (pending your approval)

```powershell
# Delete the local feature branch
git branch -d feature/event-integration

# Delete the remote feature branch
git push origin --delete feature/event-integration
```

> [!CAUTION]
> Step 7 permanently removes `feature/event-integration` from both local and remote. This is intentional — the branch's history is preserved in `main` after the merge. Only execute after confirming the merge is clean.

---

## Scope of Changes

This plan touches exactly **1 file**:

| File | Change Type | Why |
|---|---|---|
| `app.py` | **MODIFY** | Add `add_block()` calls inside 5 existing route handlers |

No new files are created. No models changes. No new dependencies.

> [!NOTE]
> `chain.py` and `models.py` are **unchanged** — they were completed in Plans 04 and 00 respectively. This plan only adds the integration hooks.

---

## Proposed Changes

---

### `app.py` — Modifications

**Full path:** `secure-mini-cloud/app.py`

Five targeted insertions into existing route handlers. **No existing logic is removed or altered** — each change adds an `add_block()` call at the correct point in the flow.

#### Import Addition

Add the `add_block` import at the top of `app.py`, alongside the existing imports:

```python
from chain import add_block   # AUDIT: blockchain event recording
```

> [!NOTE]
> `add_block` is already imported conditionally inside the genesis block seeding (line 58). This top-level import makes it available to all route handlers without repeated inline imports. The conditional import in the genesis block can remain as-is (it runs at startup before routes are called).

---

#### AUDIT-01 — Upload Event

**Route:** `POST /` (the `index()` function)  
**Placement:** After `db.session.commit()` succeeds (line 162), before the flash message.

**Rationale (AUDIT-06):** The `add_block()` call is placed **after** the file has been encrypted, written to disk, and the DB row committed. If encryption or DB write fails, no audit block is created — preventing false audit entries.

```python
# --- CURRENT CODE (lines 161-164) ---
        db.session.add(new_file)
        db.session.commit()
        
        flash(f'Uploaded {file.filename} (encrypted)!', 'success')
```

```python
# --- MODIFIED CODE ---
        db.session.add(new_file)
        db.session.commit()

        # AUDIT-01: Record upload event after successful encrypt + DB write
        add_block(action="UPLOAD", actor=current_user.username, detail=file.filename)
        
        flash(f'Uploaded {file.filename} (encrypted)!', 'success')
```

---

#### AUDIT-02 — Download Event

**Route:** `GET /download/<file_uuid>` (the `download()` function)  
**Placement:** After the `send_file()` response is prepared, but since `send_file()` returns immediately as a response object, we record the event **before** the return statement (after successful decryption).

**Rationale (AUDIT-06):** The block is recorded after the file has been successfully read from disk and decrypted. If the file doesn't exist or decryption fails, the function returns an error before reaching the `add_block()` call.

```python
# --- CURRENT CODE (lines 191-198) ---
    user_fernet = Fernet(current_user.encryption_key.encode('utf-8'))
    decrypted_content = user_fernet.decrypt(encrypted_content)
    
    return send_file(
        io.BytesIO(decrypted_content), 
        as_attachment=True, 
        download_name=file_record.original_filename
    )
```

```python
# --- MODIFIED CODE ---
    user_fernet = Fernet(current_user.encryption_key.encode('utf-8'))
    decrypted_content = user_fernet.decrypt(encrypted_content)

    # AUDIT-02: Record download event after successful decryption
    add_block(action="DOWNLOAD", actor=current_user.username, detail=file_record.original_filename)
    
    return send_file(
        io.BytesIO(decrypted_content), 
        as_attachment=True, 
        download_name=file_record.original_filename
    )
```

---

#### AUDIT-03 — Delete Event

**Route:** `POST /delete/<file_uuid>` (the `delete_file()` function)  
**Placement:** After `db.session.commit()` succeeds (line 216), before the flash message.

**Rationale (AUDIT-06):** The block is recorded after the file has been removed from disk and the DB row deleted and committed. If either operation fails, no audit block is created.

```python
# --- CURRENT CODE (lines 215-218) ---
    db.session.delete(file_record)
    db.session.commit()
    
    flash('File deleted successfully.', 'success')
```

```python
# --- MODIFIED CODE ---
    db.session.delete(file_record)
    db.session.commit()

    # AUDIT-03: Record delete event after successful disk + DB removal
    add_block(action="DELETE", actor=current_user.username, detail=file_record.original_filename)
    
    flash('File deleted successfully.', 'success')
```

> [!IMPORTANT]
> We capture `file_record.original_filename` **before** the `db.session.delete()` + `commit()` call. Since the `file_record` variable was fetched earlier in the function and the filename is already in memory, this works correctly even though the DB row is deleted. The `original_filename` attribute is still accessible on the detached Python object.

---

#### AUDIT-04 — Login Failure Event

**Route:** `POST /login` (the `login()` function)  
**Placement:** Inside the `else` branch where credentials are invalid (line 107-108), before the flash message.

**Rationale (AUDIT-06):** The block is recorded only when authentication actually fails — not on GET requests or when the user is already authenticated.

```python
# --- CURRENT CODE (lines 107-108) ---
        else:
            flash('Invalid credentials', 'danger')
```

```python
# --- MODIFIED CODE ---
        else:
            # AUDIT-04: Record failed login with email attempted + client IP
            add_block(action="LOGIN_FAIL", actor=email, detail=request.remote_addr)
            flash('Invalid credentials', 'danger')
```

> [!NOTE]
> The `actor` field uses the `email` variable (the email address the user attempted to log in with), not a username — because on a failed login we don't have a valid user object. The `detail` field captures `request.remote_addr` (the client's IP address) for forensic value.

---

#### AUDIT-05 — Login Success Event

**Route:** `POST /login` (the `login()` function)  
**Placement:** After `login_user(user)` succeeds (line 104), before the flash message.

**Rationale (AUDIT-06):** The block is recorded after `login_user()` has successfully created the session. If `login_user()` were to raise an exception (unlikely but possible), the audit block would not be recorded.

```python
# --- CURRENT CODE (lines 103-106) ---
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
```

```python
# --- MODIFIED CODE ---
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            # AUDIT-05: Record successful login with username + client IP
            add_block(action="LOGIN", actor=user.username, detail=request.remote_addr)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
```

---

## Complete Modified `app.py` Summary

After all five insertions, the route handler structure looks like this:

| Route | Event | `add_block()` Placement | Actor | Detail |
|---|---|---|---|---|
| `POST /` (upload) | `UPLOAD` | After `db.session.commit()` | `current_user.username` | `file.filename` (original name) |
| `GET /download/<uuid>` | `DOWNLOAD` | After successful decryption | `current_user.username` | `file_record.original_filename` |
| `POST /delete/<uuid>` | `DELETE` | After `db.session.commit()` | `current_user.username` | `file_record.original_filename` |
| `POST /login` (fail) | `LOGIN_FAIL` | Inside `else` branch | `email` (attempted) | `request.remote_addr` |
| `POST /login` (success) | `LOGIN` | After `login_user(user)` | `user.username` | `request.remote_addr` |

---

## NFR Compliance

| NFR | How This Plan Satisfies It |
|---|---|
| NFR-06 (Append-Only) | `add_block()` only calls `db.session.add()` — no UPDATE/DELETE on `blockchain_ledger` |
| NFR-09 (Graceful Degradation) | `add_block()` in `chain.py` wraps all DB operations in `try/except` — if the block fails to write, the primary route operation still completes |

---

## Verification Checklist

Work through this checklist on the `feature/event-integration` branch before approving the commit.

### AUDIT-01 — Upload Event
- [ ] Upload a file → open DB → confirm a new block exists with `action="UPLOAD"`, `actor=<your username>`, `detail=<original filename>`
- [ ] Upload a second file → confirm block index increments and `previous_hash` matches the prior block's `hash`

### AUDIT-02 — Download Event
- [ ] Download a file → confirm a block with `action="DOWNLOAD"`, `actor=<your username>`, `detail=<original filename>`

### AUDIT-03 — Delete Event
- [ ] Delete a file → confirm a block with `action="DELETE"`, `actor=<your username>`, `detail=<original filename>`
- [ ] The `detail` field contains the correct filename (not UUID or stored name)

### AUDIT-04 — Login Failure Event
- [ ] Attempt login with wrong password → confirm a block with `action="LOGIN_FAIL"`, `actor=<email attempted>`, `detail=<IP address>`
- [ ] The `actor` is the email address, not a username

### AUDIT-05 — Login Success Event
- [ ] Log in successfully → confirm a block with `action="LOGIN"`, `actor=<username>`, `detail=<IP address>`

### AUDIT-06 — Placement Correctness
- [ ] Force a file upload to fail (e.g., unsupported extension) → confirm NO audit block is created for the failed attempt
- [ ] Confirm all `add_block()` calls in `app.py` come AFTER the primary operation succeeds
- [ ] Confirm `add_block()` is never called at import time or outside a route handler

### Chain Integrity After Events
- [ ] After performing several operations (login, upload, download, delete), run `verify_chain()` → confirm `(True, None)`

```powershell
# Quick verification from project root (PowerShell)
python -c "
from app import app
from models import BlockchainLedger
from chain import verify_chain
with app.app_context():
    blocks = BlockchainLedger.query.order_by(BlockchainLedger.id.asc()).all()
    print(f'Total blocks: {len(blocks)}')
    print()
    for b in blocks:
        print(f'  Block #{b.id}: {b.action:12s} actor={b.actor!r:20s} detail={b.detail!r}')
    print()
    ok, broken_at = verify_chain()
    print(f'Chain intact: {ok} | Broken at: {broken_at}')
"
```

### NFR-09 — Graceful Degradation
- [ ] Confirm that if `add_block()` raises an exception internally, the route still completes (e.g., upload still succeeds, user still gets flash message)

### Regression — All v2.0 Scenarios Still Pass
- [ ] Register a new user → success
- [ ] Login → success
- [ ] Upload a file → encrypted blob appears in `uploads/<user_id>/`
- [ ] Download own file → original bytes received
- [ ] Attempt to download another user's file → HTTP 403
- [ ] Delete own file → blob removed from disk, row gone from `files`

---

## Commit, Merge & Cleanup (Requires Your Approval at Each Step)

### Step A — Commit & Push Feature Branch

Once all checklist items are green:

```powershell
git add app.py
git commit -m "feat(audit): wire add_block() into all route handlers (AUDIT-01 to AUDIT-06)

- AUDIT-01: UPLOAD event after successful encrypt + DB write
- AUDIT-02: DOWNLOAD event after successful decrypt + stream
- AUDIT-03: DELETE event after successful disk + DB removal
- AUDIT-04: LOGIN_FAIL event with email + IP on bad credentials
- AUDIT-05: LOGIN event with username + IP on successful auth
- AUDIT-06: All add_block() calls placed after primary operation succeeds"

git push -u origin feature/event-integration
```

### Step B — Merge to Main

```powershell
git checkout main
git merge feature/event-integration
git push origin main
```

### Step C — Delete Feature Branch (Permanent)

```powershell
# Delete local branch
git branch -d feature/event-integration

# Delete remote branch
git push origin --delete feature/event-integration
```

> [!WARNING]
> After Step C, `feature/event-integration` is gone from both local and remote. All history is preserved in `main`. This step is irreversible.

---

## File Tree After This Plan

```
secure-mini-cloud/
├── chain.py                        ← UNCHANGED (completed in Plan 04)
├── models.py                       ← UNCHANGED (completed in Plan 00)
├── config.py                       ← UNCHANGED
├── app.py                          ← MODIFIED (5 add_block() calls added)
├── plans/
│   ├── 00-database-foundation.md
│   ├── 04-blockchain-core-module.md
│   └── 05-event-integration.md     ← THIS PLAN
├── static/style.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   └── register.html
├── instance/secure_cloud.db
├── uploads/
├── requirements.txt                ← UNCHANGED (no new dependencies)
└── README.md
```

---

## What This Plan Does NOT Cover

These are handled in separate plans:

| Section | Plan |
|---|---|
| 4.3 Admin Dashboard (ADMIN-01 to ADMIN-06) | `06-admin-dashboard.md` |
| README.md blockchain section update | Included in `06-admin-dashboard.md` |
| Demo Scenario 5 (tamper detection) | Included in `06-admin-dashboard.md` |
