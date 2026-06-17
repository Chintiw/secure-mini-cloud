# SPEC-001: Full UI Overhaul — Implementation Plan

**Spec:** [001-ui-overhaul.md](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/spec/001-ui-overhaul.md)  
**Design Authority:** [DESIGN.md](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/DESIGN.md)  
**Scope:** Full rewrite of `style.css`, `base.html`, `login.html`, `register.html`, `index.html`; minor update to `admin.html`; 2 new error templates + 2 error handlers in `app.py`

---

## User Review Required

> [!IMPORTANT]
> **This is a frontend-only overhaul.** No database migrations, no route changes, no new dependencies. The running Flask server (`python app.py`) will pick up template/CSS changes on refresh. The only backend change is 2 new `@app.errorhandler` registrations in `app.py` (8 lines).

> [!WARNING]
> **`style.css` is a full rewrite** — the entire 818-line file will be replaced. All dark glassmorphism variables (`--bg-color`, `--card-bg`, `--border-color`, `--text-primary`, `--text-secondary`, `--accent-color`, etc.) will be removed. The `.admin-surface` scoped token override is also removed in favor of global `:root` tokens. If you have any custom CSS extensions outside of the tracked files, they may break.

> [!IMPORTANT]
> **The app server is currently running** (`python app.py` in terminal). We'll work on a feature branch and you can live-reload to see changes. Once you confirm, we merge to `main` and prune the branch.

---

## Open Questions

> [!IMPORTANT]
> **Password strength indicator (Spec §7.3):** The spec marks this as "Optional/Enhancement." Should I implement it in this pass, or defer?

> [!IMPORTANT]
> **Mobile hamburger navigation (Spec §13.3):** The spec calls for a full-screen overlay menu on `< 600px` with a hamburger icon. This requires ~30 lines of JS for toggle behavior. Should I implement the full mobile nav, or keep it simpler (horizontal scroll / wrapping links) for now?

> [!IMPORTANT]
> **Drag-and-drop upload JS (Spec §8.4):** The spec describes an enhanced dropzone with drag-over states. The visual CSS is straightforward, but actual JS drag-and-drop file handling is listed as "Out of Scope" in §17. Should I implement just the CSS visual enhancement (dashed border, hover states) wrapping the existing `<input type="file">`, or also add JS drag-drop behavior?

---

## Git Workflow

The entire overhaul will be done on a feature branch. The workflow is:

```
main ──→ feature/ui-overhaul ──→ (all work here) ──→ merge to main ──→ delete branch
```

### Steps:
1. **Create feature branch:** `git checkout -b feature/ui-overhaul`
2. **Make all changes** on `feature/ui-overhaul` (Phases 2–6 below)
3. **Commit incrementally** per phase with descriptive messages
4. **User reviews** the result on the running dev server
5. **On user confirmation:** `git checkout main && git merge feature/ui-overhaul`
6. **Prune feature branch:** `git branch -d feature/ui-overhaul`

---

## Proposed Changes

### Phase 1 — Git Setup

Create the feature branch and establish the working context.

```bash
git checkout -b feature/ui-overhaul
```

No file changes in this phase.

---

### Phase 2 — CSS Design System Rewrite

#### [MODIFY] [style.css](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/static/style.css)

**Full rewrite** — replace all 818 lines. The new CSS will contain:

**2a. `:root` Token Definitions (~80 lines)**
- All color tokens from Spec §4.1 (surface, text, border, brand, semantic, accent, gradient pairs)
- Typography tokens (`--font-sans`, `--font-mono`)
- Spacing scale (4px base, `--space-xxs` through `--space-4xl`)
- Radius scale (`--radius-xs` through `--radius-full`)
- Elevation shadows (`--shadow-level-1` through `--shadow-level-5`)
- Remove ALL dark glassmorphism variables (`--bg-color`, `--card-bg`, `--border-color`, etc.)
- Remove ALL `.admin-surface` scoped variables (`--admin-canvas`, `--admin-ink`, etc.)

**2b. Global Reset & Typography Classes (~60 lines)**
- `body`: `background: var(--canvas-soft)`, `color: var(--ink)`, `font-family: var(--font-sans)`
- Typography utility classes per Spec §4.2: `.display-xl`, `.display-lg`, `.display-md`, `.display-sm`, `.body-lg`, `.body-md`, `.body-sm`, `.caption`, `.caption-mono`, `.code`, `.button-md`, `.button-lg`
- Global `a` styles: `color: var(--link)`, underline on hover

**2c. Component Classes (~250 lines)**
- **Nav bar:** `.nav-bar`, `.nav-logo`, `.nav-links`, `.nav-cta-signup`, `.nav-cta-login`, `.nav-admin-cta` — per Spec §5.3
- **Buttons:** `.btn-primary`, `.btn-secondary`, `.btn-primary-sm`, `.btn-secondary-sm`, `.btn-danger-sm` — per DESIGN.md button specs
- **Form inputs:** `.form-input` — per Spec §6.2 (40px height, hairline border, focus glow)
- **Cards:** `.stat-card`, `.upload-card`, `.table-card`, `.auth-card`, `.error-card` — per Spec §§6–10
- **Toast system:** `.toast-container`, `.toast`, `.toast-success`, `.toast-danger`, `.toast-info` — per Spec §5.4 with auto-dismiss
- **Footer:** `.site-footer` — per Spec §5.5
- **Skip link:** `.skip-link` — per Spec §5.6
- **Page header:** `.page-header`, `.page-eyebrow` — shared between dashboard + admin
- **Auth gradient:** `.auth-gradient-backdrop` — per Spec §6.3
- **Upload dropzone:** `.upload-dropzone` — per Spec §8.4
- **File table:** reusable table styles from `ex-data-table-cell` — per Spec §8.5
- **Empty state:** `.empty-state` — per Spec §8.5
- **Badge:** `.badge-secondary`, `.action-badge`, `.action-*` variants — carry forward from admin
- **Integrity banner:** `.integrity-banner` variants — carry forward, update token refs

**2d. Admin-Specific Classes (~50 lines)**
- Keep `.admin-header`, `.admin-title`, `.admin-subtitle`, `.admin-eyebrow`, `.admin-stat-card`, etc.
- **Change:** All `var(--admin-*)` references → `var(--*)` (global tokens)
- Remove `.admin-surface` wrapper styling entirely

**2e. Animations & Keyframes (~40 lines)**
- All wrapped in `@media (prefers-reduced-motion: no-preference)`
- `@keyframes fadeInUp` — page load animation (Spec §12)
- `@keyframes slideInRight` — toast entrance
- `@keyframes slideOutRight` — toast exit
- `@keyframes bannerSlideIn` — integrity banner entrance
- Hover transitions on buttons, inputs, table rows

**2f. Responsive Breakpoints (~80 lines)**
- `@media (max-width: 600px)` — mobile: stacked metrics grid, full-width auth cards, responsive nav, card-based admin ledger
- `@media (min-width: 600px) and (max-width: 959px)` — tablet: 2-up metrics
- `@media (min-width: 960px)` — desktop: full 3-up grid, max-width containers

**Estimated total:** ~560 lines (down from 818 — the removal of duplicate `.admin-surface` scoping saves significant LOC)

---

### Phase 3 — Base Shell Rewrite

#### [MODIFY] [base.html](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/base.html)

**Full rewrite** of the 47-line shell. New structure:

**3a. `<head>` Updates**
- Add `<meta name="description">` — SEO (Spec §5.1)
- Add `<meta name="theme-color" content="#fafafa">` — mobile browser chrome
- Add Google Fonts `<link>` for Inter (400/500/600) + JetBrains Mono (400) with `preconnect` (Spec §5.1)
- Dynamic `<title>`: `{% block title %}SecureCloud{% endblock %} — Encrypted File Storage` (Spec §5.2)

**3b. Navigation Bar Redesign**
- Sticky 64px nav with `backdrop-filter: blur(12px)`, `background: rgba(255,255,255,0.85)` (Spec §5.3)
- Logo: "Secure" in `--ink` + "Cloud" in `--link` with 🔒 prefix
- Authenticated state: `Welcome, {username}` + optional Admin purple pill + Logout button
- Unauthenticated state: "Login" text link + "Register" ink-bg pill
- Remove all inline `style=""` attributes

**3c. Flash Messages → Toast System**
- Fixed position, top-right (Spec §5.4)
- Left accent border per category (`--link` for success, `--error` for danger, `--violet` for info)
- Slide-in animation + **auto-dismiss after 4s** with fade-out (currently missing)
- Inline `<script>` (~10 lines) for auto-dismiss `setTimeout`

**3d. Footer Addition**
- New `<footer>` below `</main>` (Spec §5.5)
- "SecureCloud v3.0 · Encrypted File Storage with Blockchain Audit"
- "© 2026 SecureCloud"
- Hairline top border, centered layout

**3e. Skip Link**
- Keep existing skip link, ensure it's styled per DESIGN.md (ink bg, white text, visible on `:focus-visible`)

**3f. Semantic Wrapper**
- Wrap nav in `<header>`, content in `<main id="main-content">`, footer in `<footer>`

---

### Phase 4 — Auth Pages

#### [MODIFY] [login.html](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/login.html)

**Full rewrite** of the 22-line template:

- Add `{% block title %}Login{% endblock %}`
- Mesh gradient backdrop div (`.auth-gradient-backdrop`) — Spec §6.3
- Auth card (`.auth-card`): centered, max-width 420px, `shadow-level-5`
- 🔒 lock icon, "Welcome back." headline (`display-md`), "Sign in to your encrypted vault" subtitle (`body-md`)
- Proper `<label for="">` + `<input id="">` pairs with unique IDs (`id="login-email"`, `id="login-password"`)
- Submit: "Login Securely" pill button, full-width, `--primary` bg
- Secondary: "Don't have an account? Register here" with `--link` color
- Remove all `style=""` inline attributes
- Remove `.glass-card` class usage

---

#### [MODIFY] [register.html](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/register.html)

**Full rewrite** of the 26-line template — mirrors login structure with:

- `{% block title %}Register{% endblock %}`
- Same mesh gradient + auth card
- "Create your vault." headline, "Your files, encrypted and isolated" subtitle
- Three fields: Username, Email, Password (with unique IDs: `id="reg-username"`, `id="reg-email"`, `id="reg-password"`)
- "Create Account" CTA
- "Already have an account? Login here" secondary link
- *(Password strength indicator — pending your answer to the Open Question)*

---

### Phase 5 — Dashboard

#### [MODIFY] [index.html](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/index.html)

**Full rewrite** of the 62-line template:

**5a. Page Header**
- `{% block title %}Dashboard{% endblock %}`
- "Your encrypted vault." headline (`display-lg`)
- "DASHBOARD · SecureCloud v3.0" eyebrow (`caption-mono`)

**5b. Metrics Cards (3-up)**
- Add a third card: "ENCRYPTION" → "AES-128" in `--link` color (static label, no backend change)
- Each card: `.stat-card` with `caption-mono` label + `display-md` value
- 3-column grid, responsive to 1-up on mobile

**5c. Upload Section**
- Card wrapper with `caption-mono` "SECURE UPLOAD" label
- Enhanced dropzone: dashed border, centered upload icon (`↑`), hint text, file-type badges
- Existing `<form>` + `<input type="file">` preserved (just restyled)
- "Encrypt & Upload" pill button, full width

**5d. File Table**
- Card wrapper with `caption-mono` "YOUR FILES" header + sort hint
- `<table>` with proper `<thead>/<tbody>`, `aria-label="Your files"`
- File name with type emoji prefix (📄)
- Size in `font-mono`, date in `font-mono` truncated to `MMM DD`
- Download: white pill with hairline border
- Delete: `--error` text, `--error-soft` border, red fill on hover
- Remove all `style=""` inline attributes

**5e. Empty State**
- Replace plain text with `.empty-state` card: lock icon, "Your vault is empty." body, "Upload your first file" CTA link

**5f. Jinja Variables Preserved**
- `{{ files|length }}`, `{{ files|sum(attribute='file_size')|filesizeformat }}`, `{{ file.original_filename }}`, `{{ file.file_size|filesizeformat }}`, `{{ file.uploaded_at.strftime(...) }}`, `{{ url_for('download', ...) }}`, `{{ url_for('delete_file', ...) }}`
- No backend changes needed

---

### Phase 6 — Admin + Error Pages + Backend

#### [MODIFY] [admin.html](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/admin.html)

**Minor update** to the 127-line template:

- Add `{% block title %}Admin — Audit Ledger{% endblock %}`
- Remove `.admin-surface` wrapper `<div>` — content goes directly in `{% block content %}`
- Remove the duplicate skip link (now in `base.html`)
- Update headline to sentence-case: "Admin dashboard." (period-terminated per Spec §3.2, Principle 10)
- Keep all existing ARIA attributes, `role`, `scope="col"`, `data-broken`
- Keep all Jinja variables unchanged

---

#### [NEW] [403.html](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/403.html)

New template (~20 lines):

- Extends `base.html`, `{% block title %}Forbidden{% endblock %}`
- Centered `.error-card`: 🛡️ shield icon (48px, `--error`), "Access denied." headline, "You don't have permission to view this page." body
- "Back to Dashboard" CTA → `{{ url_for('index') }}`

---

#### [NEW] [404.html](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/404.html)

New template (~20 lines):

- Extends `base.html`, `{% block title %}Not Found{% endblock %}`
- Centered `.error-card`: 🔍 magnifier icon (48px, `--mute`), "Page not found." headline, "The page you're looking for doesn't exist." body
- "Back to Dashboard" CTA → `{{ url_for('index') }}`

---

#### [MODIFY] [app.py](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/app.py)

**Add 2 error handlers** after the existing `@app.errorhandler(413)` block (~8 lines):

```python
@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
```

This ensures `abort(403)` from `admin_required` renders our custom page, and any 404s get the branded template.

---

### Phase 7 — Git Finalize

After all phases are complete and you've confirmed the result:

```bash
git checkout main
git merge feature/ui-overhaul
git branch -d feature/ui-overhaul
```

If remote tracking is active:
```bash
git push origin main
git push origin --delete feature/ui-overhaul
```

---

## Summary of File Changes

| File | Action | Lines (est.) |
|---|---|---|
| [style.css](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/static/style.css) | Full rewrite | 818 → ~560 |
| [base.html](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/base.html) | Full rewrite | 47 → ~75 |
| [login.html](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/login.html) | Full rewrite | 22 → ~40 |
| [register.html](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/register.html) | Full rewrite | 26 → ~48 |
| [index.html](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/index.html) | Full rewrite | 62 → ~95 |
| [admin.html](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/admin.html) | Minor update | 127 → ~120 |
| [403.html](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/403.html) | **NEW** | ~20 |
| [404.html](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/404.html) | **NEW** | ~20 |
| [app.py](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/app.py) | Add 2 handlers | +8 lines |

**Total estimated new LOC:** ~980  
**Files untouched:** `models.py`, `chain.py`, `config.py`, `requirements.txt`

---

## Verification Plan

### Automated Tests
No automated test suite exists. All verification is manual.

### Manual Verification

| Check | Method |
|---|---|
| Light theme everywhere | No `#0f172a` dark backgrounds visible on any page |
| Google Fonts loaded | DevTools → Network → verify Inter + JetBrains Mono requests |
| Typography | Headings in Inter 600, hashes/timestamps in JetBrains Mono |
| Login flow | Register → Login → Dashboard → Logout — all functional |
| File operations | Upload → appears in table → Download → Delete |
| Admin access | Admin user → Admin page loads with ledger, correct tokens |
| Non-admin 403 | Non-admin hitting `/admin` → custom 403 page |
| 404 page | Hit `/nonexistent` → custom 404 page |
| Flash auto-dismiss | Upload success → toast slides in → auto-dismisses after 4s |
| Responsive (375px) | Mobile layout: stacked metrics, full-width cards |
| Responsive (768px) | Tablet layout |
| Responsive (1440px) | Desktop layout, max-width containers |
| Reduced motion | Toggle `prefers-reduced-motion: reduce` → animations instant |
| Skip link | Tab on page load → skip link visible |
| Keyboard nav | Tab through all interactive elements → focus ring visible |
| Page titles | Each page shows unique `<title>` in browser tab |

### Post-Merge
- Verify `main` branch has all changes
- Verify feature branch is deleted
- One final full walkthrough on `main`
