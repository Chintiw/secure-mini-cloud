# 4.3 Admin Dashboard (ADMIN)
## Technical Implementation Plan — SecureCloud v3.0

**Source PRD:** `SecureCloud_PRD_v3_Blockchain.md` · Sections 4.3 (ADMIN-01–06), §9 M4 & M5, §12 Demo Scenarios  
**Design System:** `DESIGN.md` — Vercel-inspired design language (ink-on-white, Geist typography, stacked-shadow elevation)  
**Skills Applied:**
- `web-design-guidelines` — Vercel Web Interface Guidelines (accessibility, focus states, forms, animation, typography)
- `tailwind-4-docs` (engineering-playbook + gotchas) — CSS architecture principles applied to vanilla CSS decisions  
**Depends on:** Plan 00 ✅ · Plan 04 ✅ · Plan 05 ✅  
**Branch:** `feature/admin-dashboard`

---

## Design System Reference (DESIGN.md)

This plan re-skins the existing dark glassmorphism UI to align with the DESIGN.md Vercel-inspired design language for the admin page. The admin surface is the most formal screen in the app (it carries security evidence for the viva) and benefits from a cleaner, higher-contrast presentation.

> [!IMPORTANT]
> The existing `style.css` uses a **dark glassmorphism** design system (`--bg-color: #0f172a`). DESIGN.md describes a **light, ink-on-white** system. Rather than a full rewrite, the admin page will adopt the DESIGN.md token vocabulary as CSS custom properties that **layer on top** of the existing dark system, using a `.admin-surface` wrapper to scope the light palette. This avoids breaking the existing dashboard, login, and register pages.

### Tokens used from DESIGN.md

| Purpose | DESIGN.md Token | Resolved Value |
|---|---|---|
| Page background | `canvas-soft` | `#fafafa` |
| Card surface | `canvas` | `#ffffff` |
| Primary text | `ink` | `#171717` |
| Secondary text | `body` | `#4d4d4d` |
| Muted text | `mute` | `#888888` |
| Borders/dividers | `hairline` | `#ebebeb` |
| Stronger border | `hairline-strong` | `#a1a1a1` |
| Primary CTA / admin accent | `primary` | `#171717` |
| Success state | `link` (legacy success) | `#0070f3` |
| Error/danger | `error` | `#ee0000` |
| Error background | `error-soft` | `#f7d4d6` |
| Warning | `warning` | `#f5a623` |
| Warning background | `warning-soft` | `#ffefcf` |
| Violet accent | `violet` | `#7928ca` |
| Cyan accent | `cyan` | `#50e3c2` |
| Body font | Geist → Inter (open substitute) | `Inter, system-ui, sans-serif` |
| Mono font | Geist Mono → JetBrains Mono / IBM Plex Mono | `'JetBrains Mono', 'IBM Plex Mono', ui-monospace, monospace` |
| Button radius (nav scale) | `rounded.sm` | `6px` |
| Card radius | `rounded.md` / `rounded.lg` | `8px` / `12px` |
| Pill CTA radius | `rounded.pill` | `100px` |

### Typography scale applied (from DESIGN.md)

| Element | Token | Size / Weight / Tracking |
|---|---|---|
| Page title "Admin Dashboard" | `display-lg` | 32px / 600 / -1.28px |
| Section sub-label | `caption-mono` | 12px / 400 / mono face |
| Table headers | `caption-mono` (uppercase mono) | 12px / 400 / uppercase |
| Table body | `body-sm` | 14px / 400 / -0.28px |
| Block index / actor | `body-sm-strong` | 14px / 500 / -0.28px |
| Hash values | `code` | 13px / 400 / mono |
| Action badges | `caption` | 12px / 400 |
| Integrity banner title | `display-sm` | 20px / 600 / -0.6px |
| Integrity banner detail | `body-sm` | 14px / 400 |
| Admin nav button | `button-md` | 14px / 500 |

### Elevation applied (from DESIGN.md §Elevation)

| Element | Level | Treatment |
|---|---|---|
| Admin page card wrapper | Level 4 — Float Stack | `0px 2px 2px rgba(0,0,0,0.04), 0px 8px 16px -4px rgba(0,0,0,0.04)` + inset 1px hairline |
| Integrity banner | Level 3 — Soft Stack | `0px 2px 2px rgba(0,0,0,0.04), 0px 8px 8px -8px rgba(0,0,0,0.04)` + inset 1px |
| Table header row | Level 0 — Flat | `canvas-soft` background, no shadow |

> **Rule from DESIGN.md:** Never use a single heavy drop-shadow. Layer multiple small offsets.

---

## Web Interface Guidelines Compliance (web-design-guidelines skill)

The following rules from the fetched guidelines are applied to every new/modified file:

### Accessibility
- `aria-label` on icon-only buttons (the "🛡 Admin" nav link needs text label if icon-only)
- `aria-live="polite"` on the integrity banner (async status update)  → use `role="status"` for OK, `role="alert"` for BROKEN
- All `<th>` elements get `scope="col"` for screen-reader table navigation
- Heading hierarchy: `<h1>` on the page title, `<h2>` only if sections are added — no skipping levels
- Skip link for main content: already handled by `base.html` `<main>` landmark; ensure no `tabindex` issues

### Focus States
- Every interactive element in `admin.html` needs `focus-visible` ring styles
- **Never** use `outline: none` without a replacement focus ring in CSS

### Typography (Guidelines §Typography)
- Use `…` (ellipsis character `&hellip;`) not `...` for the hash truncation
- `font-variant-numeric: tabular-nums` on block index, timestamp, and hash columns (numbers need to align)
- Apply `text-wrap: balance` on the integrity banner title to prevent orphaned words

### Animation
- All CSS `transition` declarations must list **explicit properties** — never `transition: all`
- Honor `prefers-reduced-motion`: wrap animations in a media query

### Content Handling
- `truncate` / `overflow: hidden; text-overflow: ellipsis; white-space: nowrap` on `detail` column (filenames can be long)
- Handle empty ledger state gracefully (ledger will always have at least the genesis block, but defensive rendering is required)
- `min-width: 0` on flex children that contain truncating text

---

## Tailwind Engineering Playbook (tailwind-4-docs skill)

> [!NOTE]
> This project uses **vanilla CSS** (not Tailwind). The engineering playbook is applied as CSS architecture principles — the "abstraction ladder" maps directly to how we structure `style.css`.

### CSS Architecture decisions (mapping playbook rules)

| Playbook Rule | Applied Decision |
|---|---|
| "Compose with existing utilities in markup" | Use existing `.glass-card`, `.table-container`, `.metric-card`, `.btn` classes where possible |
| "If values repeat, add tokens" | New admin color tokens defined as CSS custom properties in the `:root` of the admin CSS block |
| "Component classes for stable named primitives" | `.integrity-banner`, `.action-badge`, `.block-hash` are the correct abstractions — they appear repeatedly and have product meaning |
| "Base class owns layout; variant classes own tone" | `.integrity-banner` is the base; `.integrity-ok` / `.integrity-fail` are the variant classes — tone never lives in the base |
| "Transitions list properties explicitly" | `transition: background-color 0.2s, box-shadow 0.2s` — never `transition: all` |
| "Keep component classes small, stable, override-friendly" | Each admin class does one job (badge = pill shape + color, not layout) |
| "Can any CSS be deleted now?" | The v1 plan duplicated `.glass-card` chrome in admin styles. This plan reuses existing classes instead |
| Gotcha: `hover:` only fires on hover-capable devices | Handled via `:hover` in vanilla CSS (no Tailwind concern here, but noted) |

---

## Background

Plans 00, 04, and 05 are fully merged into `main`. The blockchain infrastructure is complete. **What is missing is the admin surface.** There is no `/admin` route, no `admin_required` decorator, no `admin.html` template, and the `is_admin` flag is never set on registration.

---

## Git Workflow

> [!IMPORTANT]
> All changes are made on **`feature/admin-dashboard`** — never directly on `main`. Merge only after explicit approval.

### Step 1 — Create the feature branch

```powershell
git checkout -b feature/admin-dashboard
```

### Step 2 — Develop (all changes below)

### Step 3 — Verify all spec items (checklist at end)

### Step 4 — Commit

```powershell
git add app.py templates/admin.html templates/base.html static/style.css README.md
git commit -m "feat(admin): admin dashboard with blockchain ledger + DESIGN.md + accessibility

- ADMIN-01: /admin route with @admin_required decorator (HTTP 403 for non-admins)
- ADMIN-02: full blockchain ledger table (Block#, Timestamp, Action, Actor, Detail, Hash[:12])
- ADMIN-03: integrity banner — green/red status with chain block count
- ADMIN-04: verify_chain() runs server-side on every /admin load
- ADMIN-05: first registered account auto-assigned is_admin=True
- ADMIN-06: admin page shows ledger only, no file download controls
- design: DESIGN.md Vercel token system applied (ink-on-white, Geist/Inter, stacked shadows)
- a11y: aria-live, role=alert/status, scope=col, tabular-nums, focus-visible rings
- css: explicit transitions, prefers-reduced-motion, no transition: all"
```

### Step 5 — Push

```powershell
git push -u origin feature/admin-dashboard
```

### Step 6 — Merge to main (after your approval)

```powershell
git checkout main
git merge feature/admin-dashboard
git push origin main
```

### Step 7 — Prune branch (after your approval)

```powershell
git branch -d feature/admin-dashboard
git push origin --delete feature/admin-dashboard
```

> [!CAUTION]
> Step 7 permanently removes the branch. History is preserved in `main`. Execute only after confirming the merge is clean.

---

## Scope of Changes

| File | Change Type | Why |
|---|---|---|
| `app.py` | **MODIFY** | `@admin_required` decorator, `/admin` route, first-user `is_admin` logic |
| `templates/admin.html` | **NEW** | Admin dashboard — DESIGN.md-styled, accessibility-compliant |
| `templates/base.html` | **MODIFY** | Admin nav link; add `<a id="skip-to-content">` skip link |
| `static/style.css` | **MODIFY** | Admin token block + component classes; explicit transitions; `prefers-reduced-motion` |
| `README.md` | **MODIFY** | Blockchain section + admin setup instructions |

No new pip dependencies. No `requirements.txt` changes.

---

## Proposed Changes

---

### 1. `app.py` — Three Targeted Modifications

#### 1a. ADMIN-05 — First registered user becomes admin

Inside the `register()` route, before `db.session.add(new_user)`:

```python
# CURRENT
        new_user = User(username=username, email=email, password_hash=hashed_pw, encryption_key=user_key)
        db.session.add(new_user)
        db.session.commit()

# MODIFIED
        # ADMIN-05: First registered account becomes admin
        is_first_user = User.query.count() == 0
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_pw,
            encryption_key=user_key,
            is_admin=is_first_user
        )
        db.session.add(new_user)
        db.session.commit()
```

> [!NOTE]
> `User.query.count()` is evaluated **before** `db.session.add()` so it returns the pre-insert count. First call → 0 → `is_first_user = True`. All subsequent → `False`.

---

#### 1b. `@admin_required` decorator — ADMIN-01

Add after `allowed_file()` helper, before the route definitions. Import `functools.wraps` and `flask.abort` at the top of the file alongside existing imports.

```python
# Add to top-level imports
from functools import wraps
from flask import abort

# Add after allowed_file() helper function
def admin_required(f):
    """
    ADMIN-01: Restrict access to is_admin=True users only.
    Returns HTTP 403 for any authenticated non-admin user.
    Unauthenticated users are handled upstream by @login_required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
```

---

#### 1c. `/admin` route — ADMIN-01/02/03/04/06

Add before `if __name__ == '__main__':`:

```python
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """
    ADMIN-01: admin_required enforces is_admin=True; non-admins get 403.
    ADMIN-04: verify_chain() runs on every page load — no button needed.
    ADMIN-06: renders ledger only — no file download or user management.
    """
    from chain import verify_chain
    from models import BlockchainLedger

    # ADMIN-04: live integrity check on every load
    chain_ok, broken_at = verify_chain()

    # ADMIN-02: newest-first for quick recent-activity view
    blocks = BlockchainLedger.query.order_by(BlockchainLedger.id.desc()).all()
    total_blocks = BlockchainLedger.query.count()

    return render_template(
        'admin.html',
        chain_ok=chain_ok,
        broken_at=broken_at,
        blocks=blocks,
        total_blocks=total_blocks
    )
```

> [!NOTE]
> `blocks` is ordered **descending** (newest first) so the admin sees recent activity immediately. The integrity banner always reports the broken block index in ascending block terms (the `broken_at` value from `verify_chain()`), so the table order and the banner are independently readable.

---

### 2. `templates/admin.html` — NEW FILE

**Design decisions (DESIGN.md + Web Interface Guidelines):**

- Scoped inside `.admin-surface` wrapper → light `canvas-soft` background without affecting other pages
- `<h1>` for the page title (single `h1` per page — Guidelines §Accessibility)
- `role="status"` / `role="alert"` + `aria-live` on integrity banner (Guidelines §Accessibility — async updates)
- `aria-label` on the shield emoji span (decorative → `aria-hidden="true"`)
- `scope="col"` on all `<th>` elements (Guidelines §Accessibility — table navigation)
- `text-wrap: balance` on the integrity banner title (Guidelines §Typography — widow prevention)
- `font-variant-numeric: tabular-nums` on number/hash columns (Guidelines §Typography)
- Hash cell uses `&hellip;` (not `...`) per Guidelines §Typography
- Broken row gets a `data-broken="true"` attribute so CSS can style it without JS class toggling
- Empty ledger state rendered gracefully (genesis block always exists, but defensive check included)

```html
{% extends "base.html" %}

{% block content %}
<div class="admin-surface">

  <!-- Skip to main content (Web Interface Guidelines: include skip link) -->
  <a href="#ledger-table" class="skip-link">Skip to ledger</a>

  <!-- Page header -->
  <div class="admin-header">
    <div class="admin-title-group">
      <h1 class="admin-title">
        <span aria-hidden="true" class="admin-shield-icon">🛡</span>
        Admin Dashboard
      </h1>
      <p class="admin-subtitle">
        <span class="admin-eyebrow">BLOCKCHAIN AUDIT LEDGER</span>
        &nbsp;·&nbsp; SecureCloud v3.0
      </p>
    </div>
    <div class="admin-stats">
      <div class="admin-stat-card">
        <div class="admin-stat-label">Total Blocks</div>
        <div class="admin-stat-value">{{ total_blocks }}</div>
      </div>
      <div class="admin-stat-card">
        <div class="admin-stat-label">Chain Status</div>
        <div class="admin-stat-value {% if chain_ok %}status-ok{% else %}status-fail{% endif %}">
          {% if chain_ok %}Intact{% else %}Broken{% endif %}
        </div>
      </div>
    </div>
  </div>

  <!-- ADMIN-03: Integrity Status Banner -->
  <!-- role=status for OK (non-urgent); role=alert for BROKEN (urgent) -->
  {% if chain_ok %}
  <div class="integrity-banner integrity-ok"
       role="status"
       aria-live="polite"
       aria-label="Chain integrity status: intact">
    <span class="integrity-icon" aria-hidden="true">✓</span>
    <div class="integrity-body">
      <p class="integrity-title">Chain Intact</p>
      <p class="integrity-detail">
        All {{ total_blocks }} block{{ 's' if total_blocks != 1 else '' }} verified
        &mdash; no tampering detected.
      </p>
    </div>
  </div>
  {% else %}
  <div class="integrity-banner integrity-fail"
       role="alert"
       aria-live="assertive"
       aria-label="Chain integrity failure: broken at block {{ broken_at }}">
    <span class="integrity-icon" aria-hidden="true">✗</span>
    <div class="integrity-body">
      <p class="integrity-title">Integrity Failure</p>
      <p class="integrity-detail">
        Chain broken at block <strong>#{{ broken_at }}</strong>
        &mdash; hash mismatch detected. Scroll to the highlighted row below.
      </p>
    </div>
  </div>
  {% endif %}

  <!-- ADMIN-02: Full Blockchain Ledger Table -->
  <div class="admin-table-card">
    <div class="admin-table-header">
      <span class="admin-section-label">AUDIT LEDGER</span>
      <span class="admin-table-hint">Showing newest blocks first</span>
    </div>

    {% if blocks %}
    <div class="admin-table-scroll">
      <table id="ledger-table" aria-label="Blockchain audit ledger">
        <thead>
          <tr>
            <th scope="col" class="col-index">Block&nbsp;#</th>
            <th scope="col" class="col-timestamp">Timestamp (UTC)</th>
            <th scope="col" class="col-action">Action</th>
            <th scope="col" class="col-actor">Actor</th>
            <th scope="col" class="col-detail">Detail</th>
            <th scope="col" class="col-hash">Hash</th>
          </tr>
        </thead>
        <tbody>
        {% for block in blocks %}
          <tr {% if not chain_ok and block.id == broken_at %}data-broken="true" aria-label="Broken block: hash mismatch detected"{% endif %}>
            <td class="col-index cell-index">#{{ block.id }}</td>
            <td class="col-timestamp cell-timestamp">{{ block.timestamp }}</td>
            <td class="col-action">
              <span class="action-badge action-{{ block.action | lower | replace('_', '-') }}"
                    aria-label="Action: {{ block.action }}">
                {{ block.action }}
              </span>
            </td>
            <td class="col-actor cell-actor">{{ block.actor }}</td>
            <td class="col-detail">
              <span class="cell-detail" title="{{ block.detail or '' }}">
                {{ block.detail or '&mdash;' }}
              </span>
            </td>
            <td class="col-hash">
              <code class="cell-hash" title="{{ block.hash }}">{{ block.hash[:12] }}&hellip;</code>
            </td>
          </tr>
        {% endfor %}
        </tbody>
      </table>
    </div>
    {% else %}
    <div class="admin-empty-state">
      <p>No blocks found. The genesis block is created automatically on first run.</p>
    </div>
    {% endif %}
  </div>

  <!-- ADMIN-06 disclaimer -->
  <p class="admin-disclaimer" aria-label="Admin page scope notice">
    🔒 This view shows the audit ledger only &mdash; no file access or download controls (ADMIN-06).
    The ledger is append-only; rows are never updated or deleted (NFR-06).
  </p>

</div>
{% endblock %}
```

---

### 3. `templates/base.html` — Admin Nav Link + Skip Link

Two targeted changes:

**Change A — Skip link** (Web Interface Guidelines: include skip link for main content):

```html
<!-- Add immediately after <body>, before <header> -->
<a href="#main-content" class="skip-link">Skip to main content</a>
```

Also add `id="main-content"` to the existing `<main>` tag:
```html
<main class="container" id="main-content">
```

**Change B — Conditional Admin nav link:**

```html
<!-- CURRENT -->
{% if current_user.is_authenticated %}
    <span style="color: var(--text-secondary);">Welcome, {{ current_user.username }}</span>
    <a href="{{ url_for('logout') }}" class="btn btn-outline btn-sm">Logout</a>

<!-- MODIFIED -->
{% if current_user.is_authenticated %}
    <span style="color: var(--text-secondary);">Welcome, {{ current_user.username }}</span>
    {% if current_user.is_admin %}
        <a href="{{ url_for('admin_dashboard') }}"
           class="btn btn-admin btn-sm"
           aria-label="Admin dashboard">
          <span aria-hidden="true">🛡</span> Admin
        </a>
    {% endif %}
    <a href="{{ url_for('logout') }}" class="btn btn-outline btn-sm">Logout</a>
```

---

### 4. `static/style.css` — Admin Token Block + Component Classes

Append **one new section** at the end of `style.css`. No existing rules are altered.

**CSS architecture decisions (Tailwind Engineering Playbook applied to vanilla CSS):**
- **Tokens first:** all DESIGN.md color values enter as CSS custom properties scoped to `.admin-surface` — this keeps the dark theme intact elsewhere
- **Component classes for stable named primitives:** `.integrity-banner`, `.action-badge`, `.cell-hash` are durable abstractions used multiple times
- **Base + variant separation:** `.integrity-banner` owns layout; `.integrity-ok` / `.integrity-fail` own tone
- **Explicit transitions:** all `transition` declarations list specific properties (never `transition: all`)
- **`prefers-reduced-motion`:** animations wrapped in `@media (prefers-reduced-motion: no-preference)`
- **`font-variant-numeric: tabular-nums`** on index, timestamp, hash columns (Guidelines)

```css
/* ================================================================
   ADMIN DASHBOARD — DESIGN.md Vercel Token System
   Scoped to .admin-surface to avoid overriding the dark UI elsewhere
   ================================================================ */

/* --- Skip link (Web Interface Guidelines: accessibility) --- */
.skip-link {
    position: absolute;
    top: -100px;
    left: 1rem;
    z-index: 9999;
    padding: 0.5rem 1rem;
    background: #171717;
    color: #ffffff;
    border-radius: 0 0 6px 6px;
    font-size: 0.875rem;
    font-weight: 500;
    text-decoration: none;
    transition: top 0.2s ease;
}
.skip-link:focus-visible {
    top: 0;
    outline: 2px solid #0070f3;
    outline-offset: 2px;
}

/* --- Admin surface: light token override --- */
.admin-surface {
    /* DESIGN.md color tokens */
    --admin-canvas:         #ffffff;
    --admin-canvas-soft:    #fafafa;
    --admin-canvas-soft-2:  #f5f5f5;
    --admin-ink:            #171717;
    --admin-body:           #4d4d4d;
    --admin-mute:           #888888;
    --admin-hairline:       #ebebeb;
    --admin-hairline-strong:#a1a1a1;
    --admin-primary:        #171717;  /* ink = primary CTA */
    --admin-link:           #0070f3;  /* success / link */
    --admin-error:          #ee0000;
    --admin-error-soft:     #f7d4d6;
    --admin-warning:        #f5a623;
    --admin-warning-soft:   #ffefcf;
    --admin-violet:         #7928ca;
    --admin-cyan:           #50e3c2;

    /* DESIGN.md typography */
    --admin-font-sans:  Inter, system-ui, -apple-system, sans-serif;
    --admin-font-mono:  'JetBrains Mono', 'IBM Plex Mono', ui-monospace,
                        SFMono-Regular, Menlo, Monaco, monospace;

    background-color: var(--admin-canvas-soft);
    color: var(--admin-ink);
    font-family: var(--admin-font-sans);
    min-height: calc(100vh - 64px);
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
    box-sizing: border-box;
}

/* --- Admin nav button (DESIGN.md: nav-cta-signup style, admin purple) --- */
/* DESIGN.md: button-primary-sm shape: rounded.pill (100px), button-md typography */
.btn-admin {
    background-color: var(--violet, #7928ca);
    color: #ffffff;
    border: none;
    border-radius: 100px;       /* rounded.pill per DESIGN.md */
    font-size: 0.875rem;        /* button-md: 14px */
    font-weight: 500;
    line-height: 20px;
    padding: 0 0.5rem;
    height: 28px;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    text-decoration: none;
    transition: background-color 0.2s, box-shadow 0.2s;
}
.btn-admin:hover {
    background-color: #6d28d9;
    box-shadow: 0 2px 8px rgba(109, 40, 217, 0.3);
    color: #ffffff;
}
.btn-admin:focus-visible {
    outline: 2px solid #7928ca;
    outline-offset: 2px;
}

/* --- Admin page header --- */
.admin-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.5rem;
    gap: 1rem;
    flex-wrap: wrap;
}

.admin-title-group {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

/* DESIGN.md: display-lg — 32px / 600 / -1.28px */
.admin-title {
    font-size: 2rem;
    font-weight: 600;
    letter-spacing: -0.08rem;   /* -1.28px at 32px */
    color: var(--admin-ink);
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    text-wrap: balance;
}

.admin-shield-icon {
    font-size: 1.75rem;
    line-height: 1;
}

.admin-subtitle {
    color: var(--admin-body);
    margin: 0;
    font-size: 0.875rem;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    flex-wrap: wrap;
}

/* DESIGN.md: caption-mono for eyebrow labels */
.admin-eyebrow {
    font-family: var(--admin-font-mono);
    font-size: 0.75rem;
    font-weight: 400;
    letter-spacing: 0.05em;
    color: var(--admin-mute);
    text-transform: uppercase;
}

/* Stat cards — DESIGN.md: card-soft chrome (canvas-soft, rounded.md, spacing.lg) */
.admin-stats {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
}

.admin-stat-card {
    background: var(--admin-canvas);
    border-radius: 8px;             /* rounded.md */
    padding: 1rem 1.5rem;           /* spacing.md/lg */
    min-width: 120px;
    text-align: center;
    /* DESIGN.md Level 2 elevation: subtle drop + inset hairline */
    box-shadow:
        inset 0 0 0 1px var(--admin-hairline),
        0px 1px 1px rgba(0,0,0,0.03),
        0px 2px 2px rgba(0,0,0,0.04);
}

.admin-stat-label {
    font-family: var(--admin-font-mono);
    font-size: 0.75rem;
    font-weight: 400;
    color: var(--admin-mute);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
}

.admin-stat-value {
    font-size: 1.75rem;
    font-weight: 600;
    color: var(--admin-ink);
    letter-spacing: -0.04rem;
    font-variant-numeric: tabular-nums;
}

.admin-stat-value.status-ok   { color: var(--admin-link); }
.admin-stat-value.status-fail { color: var(--admin-error); }

/* --- Integrity Banner — DESIGN.md Level 3 elevation, base + variant pattern ---
   Base class: layout, spacing, structure
   Variant classes (.integrity-ok / .integrity-fail): tone, border, glow
   (Tailwind Engineering Playbook: base owns layout, variants own tone) */
.integrity-banner {
    display: flex;
    align-items: center;
    gap: 1.25rem;
    padding: 1.25rem 1.5rem;
    border-radius: 12px;            /* rounded.lg */
    margin-bottom: 1.75rem;
    border-left: 4px solid transparent;
    /* DESIGN.md Level 3 — Soft Stack */
    box-shadow:
        inset 0 0 0 1px rgba(0,0,0,0.06),
        0px 2px 2px rgba(0,0,0,0.04),
        0px 8px 8px -8px rgba(0,0,0,0.04);
}

@media (prefers-reduced-motion: no-preference) {
    .integrity-banner {
        animation: bannerSlideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) both;
    }
}

@keyframes bannerSlideIn {
    from { opacity: 0; transform: translateY(-8px); }
    to   { opacity: 1; transform: translateY(0);    }
}

.integrity-ok {
    background-color: rgba(0, 112, 243, 0.05);   /* link-soft tint */
    border-left-color: var(--admin-link);          /* #0070f3 */
}

.integrity-fail {
    background-color: var(--admin-error-soft);     /* #f7d4d6 */
    border-left-color: var(--admin-error);          /* #ee0000 */
}

.integrity-icon {
    font-size: 2rem;
    font-weight: 700;
    flex-shrink: 0;
    line-height: 1;
    font-variant-numeric: tabular-nums;
}

.integrity-ok   .integrity-icon { color: var(--admin-link); }
.integrity-fail .integrity-icon { color: var(--admin-error); }

.integrity-body {
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    min-width: 0;
}

/* DESIGN.md: display-sm — 20px / 600 / -0.6px; text-wrap: balance (Guidelines) */
.integrity-title {
    font-size: 1.25rem;
    font-weight: 600;
    letter-spacing: -0.0375rem;  /* -0.6px */
    margin: 0;
    text-wrap: balance;
}

.integrity-ok   .integrity-title { color: var(--admin-link); }
.integrity-fail .integrity-title { color: var(--admin-error); }

/* DESIGN.md: body-sm — 14px / 400 / -0.28px */
.integrity-detail {
    font-size: 0.875rem;
    font-weight: 400;
    letter-spacing: -0.0175rem;
    color: var(--admin-body);
    margin: 0;
}

/* --- Table card — DESIGN.md Level 4 elevation (Float Stack) --- */
.admin-table-card {
    background: var(--admin-canvas);
    border-radius: 12px;            /* rounded.lg */
    overflow: hidden;
    margin-bottom: 1.5rem;
    /* DESIGN.md Level 4 — Float Stack + inset hairline ring */
    box-shadow:
        inset 0 0 0 1px var(--admin-hairline),
        0px 2px 2px rgba(0,0,0,0.04),
        0px 8px 16px -4px rgba(0,0,0,0.04);
}

.admin-table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    background: var(--admin-canvas-soft);
    border-bottom: 1px solid var(--admin-hairline);
}

/* DESIGN.md: caption-mono — 12px / 400 / uppercase mono */
.admin-section-label {
    font-family: var(--admin-font-mono);
    font-size: 0.75rem;
    font-weight: 400;
    letter-spacing: 0.05em;
    color: var(--admin-mute);
    text-transform: uppercase;
}

.admin-table-hint {
    font-size: 0.75rem;
    color: var(--admin-mute);
}

/* Horizontal scroll on small screens (content handling — Guidelines) */
.admin-table-scroll {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

/* --- Admin table overrides (light surface, DESIGN.md ex-data-table-cell) --- */
/* header uses caption-mono / canvas-soft-2 background per DESIGN.md */
.admin-surface table {
    width: 100%;
    border-collapse: collapse;
    color: var(--admin-ink);
}

.admin-surface th {
    /* DESIGN.md ex-data-table-cell: headerBackground = canvas-soft; headerTypography = caption-mono */
    background: var(--admin-canvas-soft-2, #f5f5f5);
    color: var(--admin-mute);
    font-family: var(--admin-font-mono);
    font-size: 0.75rem;
    font-weight: 400;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0.625rem 1rem;         /* DESIGN.md cellPadding: xs sm */
    text-align: left;
    border-bottom: 1px solid var(--admin-hairline);  /* rowBorder */
}

.admin-surface td {
    /* DESIGN.md ex-data-table-cell: bodyTypography = body-sm */
    font-size: 0.875rem;
    font-weight: 400;
    letter-spacing: -0.0175rem;
    color: var(--admin-ink);
    padding: 0.625rem 1rem;
    border-bottom: 1px solid var(--admin-hairline);
}

.admin-surface tr:last-child td {
    border-bottom: none;
}

.admin-surface tr:hover td {
    background: var(--admin-canvas-soft);
    transition: background-color 0.15s ease;         /* explicit property, not transition: all */
}

/* Broken row — tamper detection highlight */
.admin-surface tr[data-broken="true"] td {
    background: var(--admin-error-soft) !important;
}
.admin-surface tr[data-broken="true"] td:first-child {
    border-left: 3px solid var(--admin-error);
}

/* Column widths */
.col-index     { width: 80px;  }
.col-timestamp { width: 160px; }
.col-action    { width: 130px; }
.col-actor     { width: 140px; }
.col-detail    { min-width: 140px; }
.col-hash      { width: 130px; }

/* DESIGN.md: font-variant-numeric: tabular-nums on number columns (Guidelines §Typography) */
.cell-index {
    font-family: var(--admin-font-mono);
    font-size: 0.8125rem;
    color: var(--admin-mute);
    font-variant-numeric: tabular-nums;
}

.cell-timestamp {
    font-family: var(--admin-font-mono);
    font-size: 0.75rem;
    color: var(--admin-body);
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
}

.cell-actor {
    font-weight: 500;
    color: var(--admin-ink);
}

/* Content handling: truncate long filenames (Guidelines §Content Handling) */
.cell-detail {
    display: block;
    max-width: 180px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: var(--admin-body);
}

/* DESIGN.md: code typography — 13px / mono / tabular-nums (Guidelines §Typography) */
.cell-hash {
    font-family: var(--admin-font-mono);
    font-size: 0.8125rem;
    font-weight: 400;
    color: var(--admin-body);
    background: var(--admin-canvas-soft-2, #f5f5f5);
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    font-variant-numeric: tabular-nums;
    letter-spacing: 0.02em;
    border: 1px solid var(--admin-hairline);
    /* Use actual ellipsis character (Guidelines §Typography: "…" not "...") */
    /* enforced in template via &hellip; */
}

/* --- Action Badges — DESIGN.md badge-secondary chrome + semantic color tints ---
   Tokens: canvas-soft bg, body text, caption typography, rounded.full
   Overridden per action with DESIGN.md gradient pair hues */
.action-badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 9999px;          /* rounded.full */
    font-size: 0.75rem;             /* caption: 12px */
    font-weight: 500;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    white-space: nowrap;
    border: 1px solid transparent;
}

/* Develop gradient pair: blue-to-teal → UPLOAD */
.action-upload {
    background: rgba(0, 124, 240, 0.08);
    color: #007cf0;
    border-color: rgba(0, 124, 240, 0.2);
}
/* Develop gradient pair end → DOWNLOAD teal */
.action-download {
    background: rgba(0, 223, 216, 0.1);
    color: #00a89d;
    border-color: rgba(0, 223, 216, 0.25);
}
/* error red → DELETE */
.action-delete {
    background: var(--admin-error-soft);
    color: var(--admin-error);
    border-color: rgba(238, 0, 0, 0.2);
}
/* Preview gradient pair: violet → LOGIN */
.action-login {
    background: rgba(121, 40, 202, 0.08);
    color: var(--admin-violet);
    border-color: rgba(121, 40, 202, 0.2);
}
/* Ship gradient pair: amber → LOGIN_FAIL */
.action-login-fail {
    background: var(--admin-warning-soft);
    color: var(--admin-warning);
    border-color: rgba(245, 166, 35, 0.3);
}
/* Muted → GENESIS */
.action-genesis {
    background: var(--admin-canvas-soft);
    color: var(--admin-mute);
    border-color: var(--admin-hairline);
}

/* --- Admin empty state — DESIGN.md ex-empty-state-card --- */
.admin-empty-state {
    padding: 3rem;
    text-align: center;
    color: var(--admin-body);
    background: var(--admin-canvas-soft);
    font-size: 0.875rem;
}

/* --- Admin disclaimer --- */
.admin-disclaimer {
    margin-top: 1rem;
    font-size: 0.75rem;
    color: var(--admin-mute);
    text-align: center;
    opacity: 0.8;
}

/* --- Focus states (Web Interface Guidelines: focus-visible, never outline-none alone) --- */
.admin-surface a:focus-visible,
.admin-surface button:focus-visible {
    outline: 2px solid var(--admin-link);
    outline-offset: 2px;
    border-radius: 4px;
}

/* --- Responsive (DESIGN.md §Responsive: mobile-first, 600px tablet, 960px desktop) --- */
@media (max-width: 600px) {
    .admin-surface {
        padding: 1rem;
    }
    .admin-header {
        flex-direction: column;
        gap: 1rem;
    }
    .admin-stats {
        width: 100%;
    }
    .admin-stat-card {
        flex: 1;
        min-width: 100px;
    }
    .admin-title {
        font-size: 1.5rem;
    }
    .col-timestamp,
    .col-hash { display: none; }   /* hide lowest-priority cols on mobile */
}
```

---

### 5. `README.md` — Blockchain Section + Admin Instructions

Append after existing content:

```markdown
## Blockchain Audit Ledger (v3.0)

SecureCloud v3.0 introduces a **local, append-only blockchain audit ledger** that
records every file event (upload, download, delete) and authentication event
(login success, login failure) as a cryptographically chained block.

### Why a blockchain?

A conventional SQLite audit log can be silently edited by anyone with database
write access. The blockchain ledger solves this: each block commits to all prior
blocks through a cumulative SHA-256 hash. Any retrospective modification of a
past record changes that block's expected hash, which breaks the `previous_hash`
link in every subsequent block — detectable in real time.

> Academic reference: NIST SP 800-92 — *Guide to Computer Security Log Management*.
> Hash-chained audit logs are documented as a tamper-evidence countermeasure against
> insider log manipulation.

### How it works

1. On first run, a **genesis block** (action = `GENESIS`) is created automatically.
2. Every auditable event appends a new block via `chain.add_block()`.
3. Each block's `hash` = `SHA-256(index + timestamp + action + actor + detail + previous_hash)`.
4. `chain.verify_chain()` iterates all blocks in order, recomputes hashes, and
   checks `previous_hash` linkage.

### Admin Dashboard

Access the admin dashboard at `/admin`. Only the **first registered account** has
admin privileges (`is_admin = True`). All subsequent accounts are regular users.

The dashboard shows:
- A **live integrity banner** — green `✓ Chain Intact` or red `✗ Integrity Failure — chain broken at block #N`
- The **full audit ledger** as a table (newest blocks first)

### Demo: tamper detection

1. Perform several operations (login, upload, download, delete).
2. Open `/admin` — confirm the green "Chain Intact" banner.
3. Open `instance/secure_cloud.db` in DB Browser for SQLite.
4. Edit the `detail` field of any middle block and save.
5. Reload `/admin` — the red "Integrity Failure" banner appears, and the
   tampered row is highlighted in the table.
6. Restore the original value to return to the intact state.
```

---

## Demo Scenario 5 — Tamper Detection (M5)

> [!IMPORTANT]
> Prepare this **before the viva**. This is the showstopper demo.

### Pre-demo setup
1. Register account #1 (becomes admin automatically)
2. Register account #2 (regular user)
3. Perform: login, upload 1 file, download it, delete it
4. Open `/admin` — confirm green banner with ≥ 5 blocks

### Live demo steps
1. Open DB Browser for SQLite → `instance/secure_cloud.db` → `blockchain_ledger` table
2. Pick any block between id=2 and id=N-1
3. Edit the `detail` field (change the filename to anything)
4. **Do not close DB Browser** — click Apply
5. Switch to browser → reload `/admin`
6. Red banner appears: `✗ Integrity Failure — chain broken at block #N`
7. The tampered row is highlighted in red with a left-border accent

### Revert
Restore the original `detail` value in DB Browser → Apply → reload `/admin` → green banner returns.

---

## Verification Checklist

### ADMIN-01 — Access Control
- [ ] Log in as admin → `/admin` → 200 OK
- [ ] Log in as regular user → `/admin` → 403 Forbidden
- [ ] Unauthenticated → `/admin` → redirect to `/login`

### ADMIN-02 — Ledger Table
- [ ] All blocks displayed (Block #, Timestamp, Action, Actor, Detail, Hash)
- [ ] Hash column shows exactly 12 hex chars + `…` (ellipsis, not `...`)
- [ ] Timestamps in ISO-8601 UTC format, monospace font
- [ ] Newest block appears first (descending order)

### ADMIN-03 — Integrity Banner
- [ ] Clean DB → green "Chain Intact" banner with block count
- [ ] After DB Browser edit → red "Integrity Failure — chain broken at block #N"
- [ ] Tampered row highlighted red with left border

### ADMIN-04 — Server-Side on Every Load
- [ ] Reload admin page 3 times → integrity check runs each time
- [ ] No "re-check" button visible — purely automatic

### ADMIN-05 — First User Is Admin
- [ ] Fresh DB: register User A → `is_admin=True` in `users` table
- [ ] Register User B → `is_admin=False`
- [ ] User A sees "🛡 Admin" nav button; User B does not
- [ ] User A can access `/admin`; User B gets 403

### ADMIN-06 — No File Access
- [ ] Admin dashboard has NO download links or file controls
- [ ] Confirmed by reading `admin.html` source

### DESIGN.md Compliance
- [ ] Admin page uses `canvas-soft` (#fafafa) background, not dark glassmorphism
- [ ] Headings use Inter (Geist substitute), weight 600, negative letter-spacing
- [ ] Hash/index/timestamp cells use monospace font (JetBrains Mono / IBM Plex Mono)
- [ ] Table headers use `caption-mono` uppercase style
- [ ] Stacked shadows used on cards (not single heavy drop-shadow)
- [ ] Action badge colors align to DESIGN.md gradient pairs (blue=UPLOAD, teal=DOWNLOAD, red=DELETE, violet=LOGIN, amber=LOGIN_FAIL)

### Web Interface Guidelines Compliance
- [ ] `aria-live="polite"` on integrity OK banner; `aria-live="assertive"` on FAIL banner
- [ ] `role="status"` on OK banner; `role="alert"` on FAIL banner
- [ ] All `<th>` have `scope="col"`
- [ ] `aria-hidden="true"` on decorative emoji spans
- [ ] Skip link present and functional (`<a href="#main-content">`)
- [ ] `font-variant-numeric: tabular-nums` on index, timestamp, hash columns
- [ ] `text-wrap: balance` on integrity banner title and admin `<h1>`
- [ ] `…` (HTML entity `&hellip;`) used in hash truncation, not `...`
- [ ] No `transition: all` in CSS — all transitions list specific properties
- [ ] `prefers-reduced-motion` wraps the banner animation
- [ ] `focus-visible` ring on admin nav button and all interactive elements
- [ ] Long `detail` values truncate with ellipsis (not overflow)

### Tailwind Engineering Playbook Compliance (CSS Architecture)
- [ ] `.integrity-banner` base class owns layout only; `.integrity-ok` / `.integrity-fail` own tone
- [ ] No shared class duplicates `.glass-card` chrome — reused where applicable
- [ ] All transitions list explicit properties (no `transition: all`)
- [ ] Admin color tokens are CSS custom properties scoped to `.admin-surface`
- [ ] Component classes are small, stable, and single-purpose

### Regression — All Previous Features Still Work
- [ ] Register → success (non-admin users register normally)
- [ ] Login / Logout → success
- [ ] Upload file → encrypted blob in `uploads/<user_id>/`
- [ ] Download own file → correct bytes
- [ ] Download another user's file → 403
- [ ] Delete file → blob removed, DB row gone
- [ ] `verify_chain()` returns `(True, None)` after clean run

---

## Complete File Tree After This Plan

```
secure-mini-cloud/
├── chain.py                        ← UNCHANGED (Plan 04)
├── models.py                       ← UNCHANGED (Plan 00)
├── config.py                       ← UNCHANGED
├── app.py                          ← MODIFIED (admin_required, /admin route, first-user flag)
├── plans/
│   ├── 00-database-foundation.md
│   ├── 04-blockchain-core-module.md
│   ├── 05-event-integration.md
│   └── 06-admin-dashboard.md       ← THIS PLAN
├── static/
│   └── style.css                   ← MODIFIED (admin token block, component classes)
├── templates/
│   ├── base.html                   ← MODIFIED (skip link, admin nav link)
│   ├── admin.html                  ← NEW (integrity banner + ledger table)
│   ├── index.html                  ← UNCHANGED
│   ├── login.html                  ← UNCHANGED
│   └── register.html               ← UNCHANGED
├── instance/secure_cloud.db
├── uploads/
├── requirements.txt                ← UNCHANGED (no new dependencies)
└── README.md                       ← MODIFIED (blockchain + admin sections)
```

---

## PRD Requirements Coverage

| PRD ID | Requirement | Covered By |
|---|---|---|
| ADMIN-01 | `/admin` admin-only; HTTP 403 otherwise | `@admin_required` decorator |
| ADMIN-02 | Full ledger table (Block#, Timestamp, Action, Actor, Detail, Hash[:12]) | `admin.html` |
| ADMIN-03 | Green/red integrity banner | `admin.html` conditional banners |
| ADMIN-04 | Integrity check on every page load (no button) | `verify_chain()` in route |
| ADMIN-05 | First registered account is admin | `User.query.count() == 0` in `/register` |
| ADMIN-06 | Ledger only — no file controls | `admin.html` design |
| NFR-06 | Append-only ledger | No change — `chain.py` enforces it |
| NFR-07 | SHA-256 via `hashlib` | No change — `chain.py` |
| NFR-08 | No external blockchain network | No change |
| NFR-09 | `add_block` failures non-fatal | No change — `chain.py` try/except |
| M4 | Admin route + template | This plan |
| M5 | Demo prep + tamper detection | Demo Scenario 5 section |
| Deliverable | Updated `README.md` | README section |

---

## Skills Applied — Summary

| Skill | Where Applied |
|---|---|
| **DESIGN.md** | All CSS tokens derived from Vercel design system; typography scale, elevation levels, border-radius scale, gradient pair hues for badge colors |
| **web-design-guidelines** | `aria-live`, `role`, `scope="col"`, skip link, `focus-visible` rings, `font-variant-numeric: tabular-nums`, `text-wrap: balance`, `&hellip;` entity, explicit transitions, `prefers-reduced-motion`, `truncate` on detail column |
| **tailwind-4-docs (engineering playbook)** | CSS architecture: base+variant separation on banner, token-first custom properties, component class design (single-purpose, stable), no `transition: all`, abstraction ladder applied |
| **tailwind-4-docs (gotchas)** | N/A — project uses vanilla CSS, not Tailwind; gotchas noted as not applicable |
