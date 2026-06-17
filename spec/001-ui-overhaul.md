# SPEC-001 — Full UI Overhaul: SecureCloud v4.0

**Status:** Draft  
**Author:** Antigravity (AI pair-programmer)  
**Date:** 2026-06-17  
**Scope:** All 5 templates, `style.css` design system, `base.html` shell  
**Design Authority:** [`DESIGN.md`](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/DESIGN.md) (Vercel-inspired token system)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State Audit](#2-current-state-audit)
3. [Design Vision & Principles](#3-design-vision--principles)
4. [Design Token System](#4-design-token-system)
5. [Global Shell — `base.html`](#5-global-shell--basehtml)
6. [Page Spec: Login — `login.html`](#6-page-spec-login--loginhtml)
7. [Page Spec: Register — `register.html`](#7-page-spec-register--registerhtml)
8. [Page Spec: Dashboard — `index.html`](#8-page-spec-dashboard--indexhtml)
9. [Page Spec: Admin — `admin.html`](#9-page-spec-admin--adminhtml)
10. [Page Spec: Error Pages (403 / 404)](#10-page-spec-error-pages-403--404)
11. [Component Inventory](#11-component-inventory)
12. [Animations & Micro-interactions](#12-animations--micro-interactions)
13. [Responsive Strategy](#13-responsive-strategy)
14. [Accessibility Requirements](#14-accessibility-requirements)
15. [File Inventory & Change Map](#15-file-inventory--change-map)
16. [Verification Plan](#16-verification-plan)
17. [Out of Scope](#17-out-of-scope)

---

## 1. Executive Summary

SecureCloud's frontend currently lives in two conflicting design languages:

| Surface | Design Language | Problem |
|---|---|---|
| Auth pages + Dashboard | Dark glassmorphism (`#0f172a` bg, `rgba` cards, blur filters) | Generic dark-mode feel; no brand identity; looks like every Bootstrap dark template |
| Admin Dashboard | Light Vercel-inspired token system (DESIGN.md) | Polished, branded, but scoped only to `.admin-surface` |

The `frontend-screenshot.png` in the repo still shows the **original MVP UI** — plain white HTML with default browser-styled form controls. The current Jinja templates have improved since then with glassmorphism cards, but the visual gap between admin and user-facing pages is jarring.

### Goal

Unify the entire application under the **DESIGN.md Vercel-inspired token system** — a premium, light-mode-first design with:

- Clean `#fafafa` canvas background, `#ffffff` card surfaces
- `#171717` ink primary with the Vercel gradient palette as accent decoration
- Inter (400/500/600) for all narrative text, JetBrains Mono for technical labels
- Stacked micro-shadows (never heavy drops), hairline inset borders
- Consistent pill/square button radii at marketing and nav scale
- Smooth micro-animations with `prefers-reduced-motion` respect

### Deliverable

A complete rewrite of all 5 templates and `style.css`, eliminating the dark glassmorphism system entirely. No backend changes required — all Jinja variables, route names, and template blocks remain identical.

---

## 2. Current State Audit

### 2.1 File Inventory

| File | Lines | Current State | Verdict |
|---|---|---|---|
| [`style.css`](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/static/style.css) | 818 | Split personality: L1–306 dark glassmorphism, L307–818 admin light tokens | **Full rewrite** |
| [`base.html`](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/base.html) | 47 | Minimal shell — no `<meta description>`, no Google Fonts link, no footer | **Rewrite** |
| [`login.html`](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/login.html) | 22 | Basic form in `.glass-card`, inline styles, no icon, no branding | **Rewrite** |
| [`register.html`](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/register.html) | 26 | Copy-paste of login with one extra field, same issues | **Rewrite** |
| [`index.html`](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/index.html) | 62 | Dark-themed metric cards + table + upload form, heavy inline styles | **Rewrite** |
| [`admin.html`](file:///c:/Users/Win-Rog/Documents/Secure%20Mini%20Cloud/secure-mini-cloud/templates/admin.html) | 127 | Already follows DESIGN.md tokens — cleanest page | **Minor updates** |

### 2.2 Design System Issues

| Issue | Severity | Detail |
|---|---|---|
| **Two conflicting color systems** | Critical | `:root` dark vars (`--bg-color: #0f172a`) coexist with `.admin-surface` light vars (`--admin-canvas: #ffffff`) |
| **No Google Fonts loaded** | High | `@import` for Inter exists but JetBrains Mono is missing; Geist is referenced in DESIGN.md but not loaded |
| **Inline styles everywhere** | High | `style="margin-bottom: 1.5rem"`, `style="width: auto"`, `style="display: flex; gap: 0.5rem"` — defeats the design system |
| **No footer** | Medium | Every page ends abruptly after content — no SecureCloud branding, no copyright |
| **No page-specific `<title>`** | Medium | Every page says `<title>SecureCloud</title>` — bad for accessibility and browser tab context |
| **No skip-link in `base.html`** | Medium | Skip link exists but is only in `admin.html` — should be in the global shell |
| **Upload form is primitive** | Medium | Raw `<input type="file">` with no drag-drop affordance, no file-type visual indicator |
| **Flash messages lack auto-dismiss** | Low | Flash toasts slide in but never fade out — accumulate on screen |
| **No empty-state illustration** | Low | Empty vault shows plain text "No files uploaded yet" |
| **Screenshot is outdated** | Info | `frontend-screenshot.png` shows the original bare MVP, not the current UI |

### 2.3 What Works (Keep)

- Admin dashboard HTML structure — already follows DESIGN.md
- Jinja template blocks (`{% block content %}`)
- Route names and URL patterns
- Flash message category system (`success`, `danger`, `info`)
- Accessibility attributes in admin (ARIA labels, roles, `scope="col"`)
- Skip link pattern (extend to all pages)

---

## 3. Design Vision & Principles

### 3.1 Visual Identity

SecureCloud's UI should communicate **trust, precision, and security** through restraint — not through heavy decoration. The design language borrows from DESIGN.md's Vercel analysis:

> A developer-platform brand whose surface is a stark black-and-ink duet on near-white canvas, broken at hero scale by a multi-color mesh gradient that acts as the entire decorative system.

**Adapted for SecureCloud:**
- The mesh gradient is reserved for the **auth pages** (login/register) as a hero backdrop — establishing brand presence at the entry point
- Dashboard and admin use the **clean canvas-soft surface** with ink-on-white cards
- Security status uses the **semantic color palette** (success blue, error red, warning amber)
- Blockchain/crypto terminology rendered in **monospace face** (JetBrains Mono) to signal "technical infrastructure"

### 3.2 Design Principles

| # | Principle | Implementation |
|---|---|---|
| 1 | **Light-mode first** | `#fafafa` canvas body, `#ffffff` card surfaces. Dark mode is out of scope for v4.0 |
| 2 | **Ink is the hero** | `#171717` primary for all CTAs, headings, and data-dense text. No competing accent colors |
| 3 | **Gradient at scale only** | Auth pages get the mesh gradient backdrop. Dashboard cards never use gradients |
| 4 | **Mono for the machine** | Hash values, block indices, timestamps, file sizes — all JetBrains Mono |
| 5 | **Sans for the human** | Headlines, labels, button text, body copy — all Inter at 400/500/600 |
| 6 | **Stacked shadows, never heavy drops** | Cards use Level 2–4 elevation from DESIGN.md. No `box-shadow: 0 8px 32px rgba(0,0,0,0.2)` |
| 7 | **Negative tracking is voice** | Display headlines at `-1.28px` to `-2.4px`. Never positive letter-spacing on headings |
| 8 | **Hairline + inset ring = card edge** | Every card gets `inset 0 0 0 1px` hairline. No visible `border` property |
| 9 | **Motion is earned** | Page-load animations, hover transitions, and toast entrances. Always wrapped in `@media (prefers-reduced-motion: no-preference)` |
| 10 | **Sentence case, period-terminated** | Headlines like "Your encrypted vault." — not "YOUR ENCRYPTED VAULT" |

---

## 4. Design Token System

### 4.1 Color Tokens (CSS Custom Properties)

Replace the current `:root` dark variables with DESIGN.md light tokens as the **global** system. No `.admin-surface` scoping — these become universal.

```css
:root {
  /* ─── Surface ─── */
  --canvas:          #ffffff;
  --canvas-soft:     #fafafa;
  --canvas-soft-2:   #f5f5f5;

  /* ─── Text ─── */
  --ink:             #171717;
  --body:            #4d4d4d;
  --mute:            #888888;
  --on-primary:      #ffffff;

  /* ─── Border ─── */
  --hairline:        #ebebeb;
  --hairline-strong: #a1a1a1;

  /* ─── Brand / CTA ─── */
  --primary:         #171717;
  --link:            #0070f3;
  --link-deep:       #0761d1;

  /* ─── Semantic ─── */
  --error:           #ee0000;
  --error-soft:      #f7d4d6;
  --error-deep:      #c50000;
  --success:         #0070f3;
  --warning:         #f5a623;
  --warning-soft:    #ffefcf;

  /* ─── Accent (gradient palette) ─── */
  --violet:          #7928ca;
  --violet-soft:     #d8ccf1;
  --cyan:            #50e3c2;
  --highlight-pink:  #ff0080;

  /* ─── Gradient Pairs ─── */
  --gradient-develop-start: #007cf0;
  --gradient-develop-end:   #00dfd8;
  --gradient-preview-start: #7928ca;
  --gradient-preview-end:   #ff0080;
  --gradient-ship-start:    #ff4d4d;
  --gradient-ship-end:      #f9cb28;

  /* ─── Typography ─── */
  --font-sans: Inter, system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, monospace;

  /* ─── Spacing (4px base) ─── */
  --space-xxs: 4px;
  --space-xs:  8px;
  --space-sm:  12px;
  --space-md:  16px;
  --space-lg:  24px;
  --space-xl:  32px;
  --space-2xl: 40px;
  --space-3xl: 48px;
  --space-4xl: 64px;

  /* ─── Radii ─── */
  --radius-xs:   4px;
  --radius-sm:   6px;
  --radius-md:   8px;
  --radius-lg:   12px;
  --radius-xl:   16px;
  --radius-pill:  100px;
  --radius-full: 9999px;

  /* ─── Elevation (stacked shadows) ─── */
  --shadow-level-1: inset 0 0 0 1px rgba(0,0,0,0.08);
  --shadow-level-2: inset 0 0 0 1px rgba(0,0,0,0.08),
                    0px 1px 1px rgba(0,0,0,0.02),
                    0px 2px 2px rgba(0,0,0,0.04);
  --shadow-level-3: inset 0 0 0 1px rgba(0,0,0,0.08),
                    0px 2px 2px rgba(0,0,0,0.04),
                    0px 8px 8px -8px rgba(0,0,0,0.04);
  --shadow-level-4: inset 0 0 0 1px rgba(0,0,0,0.08),
                    0px 2px 2px rgba(0,0,0,0.04),
                    0px 8px 16px -4px rgba(0,0,0,0.04);
  --shadow-level-5: inset 0 0 0 1px rgba(0,0,0,0.08),
                    0px 1px 1px rgba(0,0,0,0.02),
                    0px 8px 16px -4px rgba(0,0,0,0.04),
                    0px 24px 32px -8px rgba(0,0,0,0.06);
}
```

### 4.2 Typography Scale

| Token Class | Size | Weight | Line Height | Letter Spacing | Font | Use |
|---|---|---|---|---|---|---|
| `.display-xl` | 48px | 600 | 48px | -2.4px | Sans | Auth page hero headlines |
| `.display-lg` | 32px | 600 | 40px | -1.28px | Sans | Page titles (Dashboard, Admin) |
| `.display-md` | 24px | 600 | 32px | -0.96px | Sans | Section headers |
| `.display-sm` | 20px | 600 | 28px | -0.6px | Sans | Card titles, banner titles |
| `.body-lg` | 18px | 400 | 28px | 0 | Sans | Lead paragraphs |
| `.body-md` | 16px | 400 | 24px | 0 | Sans | Default body text |
| `.body-sm` | 14px | 400 | 20px | -0.28px | Sans | Secondary text, nav links |
| `.caption` | 12px | 400 | 16px | 0 | Sans | Fine print |
| `.caption-mono` | 12px | 400 | 16px | 0.05em | Mono | Eyebrow labels, section labels |
| `.code` | 13px | 400 | 20px | 0 | Mono | Hashes, technical values |
| `.button-md` | 14px | 500 | 20px | 0 | Sans | Small buttons |
| `.button-lg` | 16px | 500 | 24px | 0 | Sans | Marketing CTAs |

---

## 5. Global Shell — `base.html`

### 5.1 `<head>` Additions

```html
<meta name="description" content="SecureCloud — encrypted file storage with blockchain audit ledger">
<meta name="theme-color" content="#fafafa">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
```

### 5.2 Page Title

Dynamic per-page titles via Jinja block:

```html
<title>{% block title %}SecureCloud{% endblock %} — Encrypted File Storage</title>
```

Each template overrides:
- Login: `{% block title %}Login{% endblock %}`
- Register: `{% block title %}Register{% endblock %}`
- Dashboard: `{% block title %}Dashboard{% endblock %}`
- Admin: `{% block title %}Admin — Audit Ledger{% endblock %}`

### 5.3 Navigation Bar

**Component:** `nav-bar` from DESIGN.md

| Element | Spec |
|---|---|
| Container | `height: 64px`, `background: var(--canvas)`, `border-bottom: 1px solid var(--hairline)`, `padding: var(--space-sm) var(--space-lg)`, `position: sticky; top: 0; z-index: 100` |
| Logo | "Secure" in `--ink` + "Cloud" in `--link` (`#0070f3`). Font: Inter 600, 20px. A small 🔒 lock icon before text (optional SVG) |
| Nav links (logged in) | `Welcome, {username}` in `--body` / body-sm. Separated by `·` |
| Admin CTA | Purple pill (`--violet` bg, white text, `border-radius: var(--radius-pill)`, 28px height). Only shown for `is_admin` |
| Logout button | `nav-cta-login` style (white bg, ink text, hairline border, `--radius-sm` 6px, 28px height) |
| Auth links (logged out) | "Login" as plain `--link` text link. "Register" as `nav-cta-signup` (ink bg, white text, `--radius-sm`, 28px height) |
| Backdrop filter | Subtle blur: `backdrop-filter: blur(12px); background: rgba(255,255,255,0.85)` for scroll transparency |

### 5.4 Flash Messages (Toast System)

**Component:** `ex-toast` from DESIGN.md

| Property | Spec |
|---|---|
| Position | `fixed; top: 80px; right: 20px; z-index: 1000` |
| Container | `background: var(--canvas)`, `border-radius: var(--radius-md)`, `padding: var(--space-sm) var(--space-md)`, `shadow-level-4` |
| Left accent | `border-left: 3px solid {semantic-color}` — success=`--link`, danger=`--error`, info=`--violet` |
| Typography | body-sm (14px / 400), `--ink` text |
| Animation | Slide in from right (300ms, `cubic-bezier(0.16, 1, 0.3, 1)`), auto-dismiss after 4s with fade-out |
| Max width | `380px` on desktop, `calc(100vw - 40px)` on mobile |

### 5.5 Footer

**Component:** `footer` from DESIGN.md

| Property | Spec |
|---|---|
| Background | `var(--canvas)` |
| Border top | `1px solid var(--hairline)` |
| Padding | `var(--space-xl) var(--space-lg)` |
| Layout | Centered, single row: `SecureCloud v3.0` in caption-mono + `·` + `Encrypted File Storage with Blockchain Audit` in body-sm / `--mute` |
| Copyright | `© 2026 SecureCloud` in caption / `--mute`, below |

### 5.6 Skip Link

Remains in `base.html` (moved from admin-only). Styled per DESIGN.md: ink bg, white text, `--radius-sm`, visible only on `:focus-visible`.

---

## 6. Page Spec: Login — `login.html`

### 6.1 Layout

```
┌─────────────────────────────────────────────┐
│  [nav-bar: Logo ··· Login | Register]       │
├─────────────────────────────────────────────┤
│                                             │
│       ░░░░░ MESH GRADIENT BACKDROP ░░░░░    │
│                                             │
│     ┌───────────────────────────────┐       │
│     │  🔒                          │       │
│     │  Welcome back.               │       │
│     │  Sign in to your vault       │       │
│     │                              │       │
│     │  ┌────────────────────────┐  │       │
│     │  │ Email Address          │  │       │
│     │  └────────────────────────┘  │       │
│     │  ┌────────────────────────┐  │       │
│     │  │ Password               │  │       │
│     │  └────────────────────────┘  │       │
│     │                              │       │
│     │  [████ Login Securely ████]  │       │
│     │                              │       │
│     │  Don't have an account?      │       │
│     │  Register here →             │       │
│     └───────────────────────────────┘       │
│                                             │
├─────────────────────────────────────────────┤
│  [footer]                                   │
└─────────────────────────────────────────────┘
```

### 6.2 Component Breakdown

| Element | DESIGN.md Token | Spec |
|---|---|---|
| **Page background** | `canvas-soft` | `#fafafa` with mesh gradient overlay at 15% opacity, centered, covering top 60% of viewport |
| **Auth card** | `ex-auth-form-card` | `background: var(--canvas)`, `padding: var(--space-xl)` (32px), `border-radius: var(--radius-lg)` (12px), `shadow-level-5` (modal-grade elevation), `max-width: 420px`, centered |
| **Lock icon** | — | SVG or emoji `🔒`, 32px, `--mute` color, centered above headline |
| **Headline** | `display-md` | "Welcome back." — 24px/600/-0.96px, `--ink`, sentence-case, period-terminated |
| **Subtitle** | `body-md` | "Sign in to your encrypted vault" — 16px/400, `--body` |
| **Labels** | `body-sm` | 14px/400, `--body` color |
| **Inputs** | `form-input` | `height: 40px`, `border: 1px solid var(--hairline)`, `border-radius: var(--radius-sm)` (6px), `background: var(--canvas)`, `--ink` text. Focus: `border-color: var(--link)`, `box-shadow: 0 0 0 2px rgba(0,112,243,0.15)` |
| **Submit button** | `button-primary` | `background: var(--primary)` (#171717), `color: var(--on-primary)`, `border-radius: var(--radius-pill)` (100px), `padding: 0 var(--space-sm)`, full width, 44px height, `button-lg` typography. Hover: `translateY(-1px)`, slight shadow increase |
| **Secondary link** | `link-inline` | "Register here" in `--link` (#0070f3), underline on hover |

### 6.3 Mesh Gradient Specification

The auth pages (login + register) share a decorative mesh gradient backdrop — the signature Vercel gradient adapted for SecureCloud:

```css
.auth-gradient-backdrop {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 800px;
  height: 600px;
  opacity: 0.12;
  background: radial-gradient(
    ellipse at 30% 40%,
    var(--gradient-develop-start) 0%,
    transparent 50%
  ),
  radial-gradient(
    ellipse at 70% 30%,
    var(--gradient-preview-start) 0%,
    transparent 50%
  ),
  radial-gradient(
    ellipse at 50% 60%,
    var(--gradient-preview-end) 0%,
    transparent 50%
  ),
  radial-gradient(
    ellipse at 80% 70%,
    var(--gradient-ship-end) 0%,
    transparent 50%
  );
  filter: blur(60px);
  pointer-events: none;
  z-index: 0;
}
```

The gradient must be kept at **hero scale only** per DESIGN.md rules — it is never miniaturized or used inside cards.

---

## 7. Page Spec: Register — `register.html`

### 7.1 Layout

Identical structure to Login, with one additional form field (Username).

### 7.2 Differences from Login

| Element | Login | Register |
|---|---|---|
| Headline | "Welcome back." | "Create your vault." |
| Subtitle | "Sign in to your encrypted vault" | "Your files, encrypted and isolated" |
| Fields | Email, Password | Username, Email, Password |
| CTA | "Login Securely" | "Create Account" |
| Secondary | "Don't have an account? Register here" | "Already have an account? Login here" |

### 7.3 Password Strength Indicator (Enhancement)

Optional — a visual bar below the password field:

| State | Visual |
|---|---|
| Empty | No bar visible |
| Weak (<8 chars) | `--error` red bar at 33% |
| Medium (8+ chars, mixed) | `--warning` amber bar at 66% |
| Strong (12+ chars, mixed case + number) | `--success` blue bar at 100% |

This is purely visual — the backend does no password strength validation. Implement with ~15 lines of inline JS.

---

## 8. Page Spec: Dashboard — `index.html`

### 8.1 Layout

```
┌─────────────────────────────────────────────┐
│  [nav-bar: Logo ··· Welcome, user | Admin? | Logout]  │
├─────────────────────────────────────────────┤
│                                             │
│  Your encrypted vault.                      │
│  ─ DASHBOARD ·  SecureCloud v3.0            │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Total    │  │ Storage  │  │ Security │  │
│  │ Files    │  │ Used     │  │ Status   │  │
│  │   12     │  │  4.2 MB  │  │ AES-128  │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│                                             │
│  ┌──────────────────────────────────────┐   │
│  │ SECURE UPLOAD                        │   │
│  │                                      │   │
│  │  ┌──────────────────────────────┐   │   │
│  │  │   ↑ Drag file here or click  │   │   │
│  │  │   .txt .pdf .docx .xlsx ...  │   │   │
│  │  │   Max 50 MB                  │   │   │
│  │  └──────────────────────────────┘   │   │
│  │                                      │   │
│  │  [████ Encrypt & Upload ████]       │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  ┌──────────────────────────────────────┐   │
│  │ YOUR FILES                 newest ▼  │   │
│  ├──────────────────────────────────────┤   │
│  │ 📄 report.pdf   4.2 MB  Jun 17     │   │
│  │                    [Download][Delete]│   │
│  ├──────────────────────────────────────┤   │
│  │ 📄 notes.txt    12 KB   Jun 16     │   │
│  │                    [Download][Delete]│   │
│  └──────────────────────────────────────┘   │
│                                             │
├─────────────────────────────────────────────┤
│  [footer]                                   │
└─────────────────────────────────────────────┘
```

### 8.2 Page Header

| Element | Spec |
|---|---|
| Headline | `display-lg` — "Your encrypted vault." — 32px/600/-1.28px, `--ink` |
| Eyebrow | `caption-mono` — "DASHBOARD" in uppercase mono + `·` + "SecureCloud v3.0" in `--mute` |

### 8.3 Metrics Cards (3-up)

**Component:** `admin-stat-card` pattern (extended to dashboard)

| Card | Label | Value | Icon |
|---|---|---|---|
| Total Files | `caption-mono` "TOTAL FILES" | `display-md` `{{ files\|length }}` in `--ink` | 📁 or SVG |
| Storage Used | `caption-mono` "STORAGE USED" | `display-md` `{{ total_size\|filesizeformat }}` in `--ink` | 💾 or SVG |
| Encryption | `caption-mono` "ENCRYPTION" | `display-md` "AES-128" in `--link` | 🔐 or SVG |

| Property | Spec |
|---|---|
| Background | `var(--canvas)` |
| Border radius | `var(--radius-md)` (8px) |
| Padding | `var(--space-md) var(--space-lg)` |
| Shadow | `var(--shadow-level-2)` |
| Layout | `display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-lg)` |
| Mobile | `grid-template-columns: 1fr` (stacked) |

### 8.4 Upload Section

**Component:** Custom, built from `card-marketing` + `form-input` primitives

| Element | Spec |
|---|---|
| Card | `background: var(--canvas)`, `padding: var(--space-xl)`, `border-radius: var(--radius-lg)`, `shadow-level-3` |
| Section label | `caption-mono` — "SECURE UPLOAD" |
| Dropzone | Dashed border `2px dashed var(--hairline)`, `border-radius: var(--radius-md)`, `padding: var(--space-3xl)`, centered text. **Hover/drag-over:** `border-color: var(--link)`, faint `--link` background tint |
| Upload icon | `↑` arrow or cloud-upload SVG, 32px, `--mute` color |
| Hint text | `body-sm` — "Drag a file here, or click to browse" in `--body`. Below: `caption` — ".txt · .pdf · .docx · .xlsx · .jpg · .png · .zip — Max 50 MB" in `--mute` |
| File type pills | Small pills per allowed type (`.txt`, `.pdf`, etc.) styled as `badge-secondary` — `background: var(--canvas-soft)`, `color: var(--body)`, `caption` font, `border-radius: var(--radius-full)` |
| Submit button | `button-primary` — full width, `--primary` bg, `--on-primary` text, `--radius-pill`, 44px height |

### 8.5 File Table

**Component:** `ex-data-table-cell` from DESIGN.md

| Property | Spec |
|---|---|
| Container | `background: var(--canvas)`, `border-radius: var(--radius-lg)`, `shadow-level-4`, `overflow: hidden` |
| Table header bar | `background: var(--canvas-soft)`, `border-bottom: 1px solid var(--hairline)`, `padding: var(--space-sm) var(--space-lg)`. Label: `caption-mono` "YOUR FILES" + right-aligned sort hint in `--mute` |
| `<th>` cells | `background: var(--canvas-soft-2)`, `caption-mono` uppercase, `--mute` color |
| `<td>` cells | `body-sm`, `--ink` color |
| File name | Preceded by file-type emoji (📄 for docs, 🖼️ for images, 📦 for zip) or a small SVG icon |
| Size column | `font-mono` for the value |
| Date column | `font-mono`, truncated to `MMM DD` format |
| Action buttons | **Download:** `button-secondary-sm` (white bg, ink text, hairline border, `--radius-pill`). **Delete:** `button-secondary-sm` but `--error` text, `--error-soft` border. On hover: `--error` bg, white text |
| Row hover | `background: var(--canvas-soft)`, `transition: background-color 0.15s` |
| Empty state | `ex-empty-state-card` — centered, `padding: var(--space-3xl)`, "Your vault is empty." in `body-md` / `--body`, small lock SVG icon above, subtle "Upload your first file" CTA link in `--link` |

### 8.6 Backend Context Change

The dashboard template currently receives `files` from `app.py`. No change to route logic is needed. The third metric card ("Encryption: AES-128") is a static label — no new backend data required.

---

## 9. Page Spec: Admin — `admin.html`

### 9.1 Current State

The admin page is already the closest to DESIGN.md. It uses scoped `.admin-surface` variables, proper elevation, monospace eyebrows, and action badges with gradient-pair colors.

### 9.2 Changes Required

| Change | Rationale |
|---|---|
| **Remove `.admin-surface` scoping** | All tokens are now global `:root` — admin no longer needs its own color universe |
| **Rename CSS classes** | `--admin-canvas` → `--canvas`, `--admin-ink` → `--ink`, etc. Remove the `admin-` prefix from token references |
| **Add page title block** | `{% block title %}Admin — Audit Ledger{% endblock %}` |
| **Adjust card shadows** | Align with unified `--shadow-level-*` tokens |
| **Add subtle entry animations** | Stat cards and banner should animate in on load (stagger 50ms) |
| **Improve mobile** | Currently hides timestamp + hash columns. Instead, switch to a card-based layout for each block on mobile (< 600px) |

### 9.3 Mobile Ledger Card Layout

On screens < 600px, each blockchain block renders as a card instead of a table row:

```
┌──────────────────────────┐
│  Block #47  · UPLOAD     │
│  ────────────────────    │
│  Actor:  chinmay          │
│  Detail: report.pdf       │
│  Time:   2026-06-17T07:12 │
│  Hash:   a3f8c9d12b4e…    │
└──────────────────────────┘
```

This ensures no data is hidden on mobile — just reformatted.

---

## 10. Page Spec: Error Pages (403 / 404)

### 10.1 New Templates Required

Currently, Flask returns default error pages for 403 and 404. Create custom templates:

#### `403.html` (Forbidden)

| Element | Spec |
|---|---|
| Layout | Centered card like auth pages, no gradient |
| Icon | 🛡️ shield, 48px, `--error` color |
| Headline | `display-md` — "Access denied." |
| Body | `body-md` — "You don't have permission to view this page." |
| CTA | `button-primary` — "Back to Dashboard" → `url_for('index')` |

#### `404.html` (Not Found)

| Element | Spec |
|---|---|
| Layout | Same centered card |
| Icon | 🔍 magnifier, 48px, `--mute` color |
| Headline | `display-md` — "Page not found." |
| Body | `body-md` — "The page you're looking for doesn't exist." |
| CTA | `button-primary` — "Back to Dashboard" → `url_for('index')` |

### 10.2 Backend Registration

Add to `app.py`:

```python
@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
```

---

## 11. Component Inventory

### 11.1 Complete Component List

| Component | DESIGN.md Source | Used In |
|---|---|---|
| `nav-bar` | `components.nav-bar` | base.html (all pages) |
| `nav-link` | `components.nav-link` | base.html |
| `nav-cta-signup` | `components.nav-cta-signup` | base.html (Register btn) |
| `nav-cta-login` | `components.nav-cta-login` | base.html (Logout btn) |
| `button-primary` | `components.button-primary` | Login, Register, Dashboard, Error pages |
| `button-secondary-sm` | `components.button-secondary-sm` | File table actions |
| `button-primary-sm` | `components.button-primary-sm` | Upload CTA (if inline) |
| `form-input` | `components.form-input` | Login, Register forms |
| `card-marketing` | `components.card-marketing` | Metric cards, Upload section |
| `card-marketing-large` | `components.card-marketing-large` | Auth form card |
| `ex-data-table-cell` | `components.ex-data-table-cell` | File table, Admin ledger table |
| `ex-auth-form-card` | `components.ex-auth-form-card` | Login, Register |
| `ex-empty-state-card` | `components.ex-empty-state-card` | Empty file list |
| `ex-toast` | `components.ex-toast` | Flash messages |
| `badge-secondary` | `components.badge-secondary` | File type pills, version badges |
| `action-badge` | Custom (already in admin) | Admin ledger action column |
| `integrity-banner` | Custom (already in admin) | Admin integrity status |
| `footer` | `components.footer` | base.html (all pages) |

### 11.2 New Components (not in current CSS)

| Component | Description |
|---|---|
| `.auth-gradient-backdrop` | Mesh gradient behind login/register cards |
| `.upload-dropzone-enhanced` | Interactive drop zone with drag state |
| `.file-type-pill` | Small pill showing allowed file extensions |
| `.stat-card` | Reusable metric card (shared between dashboard + admin) |
| `.page-header` | Headline + eyebrow combo (shared between dashboard + admin) |
| `.footer` | Global footer |
| `.error-card` | Centered error card for 403/404 pages |

---

## 12. Animations & Micro-interactions

All animations wrapped in `@media (prefers-reduced-motion: no-preference)`.

| Animation | Trigger | Spec |
|---|---|---|
| **Page fade-in** | Page load | `opacity: 0 → 1`, `translateY(8px) → 0`, 350ms, `cubic-bezier(0.16, 1, 0.3, 1)` |
| **Card stagger** | Page load | Metric cards + table card animate in with 50ms stagger per card |
| **Toast slide-in** | Flash message | Slide from right (200px → 0), 300ms, auto-dismiss fade after 4s |
| **Toast slide-out** | Auto-dismiss | `opacity: 1 → 0`, `translateX(0 → 100px)`, 250ms |
| **Button hover lift** | `:hover` on primary buttons | `translateY(-1px)`, shadow increase, 200ms |
| **Input focus glow** | `:focus-visible` on inputs | `box-shadow: 0 0 0 2px rgba(0,112,243,0.15)`, `border-color: var(--link)`, 200ms |
| **Dropzone drag-over** | File dragged over upload zone | `border-color: var(--link)`, faint blue bg tint, scale(1.01), 200ms |
| **Row hover** | Table row `:hover` | `background: var(--canvas-soft)`, 150ms |
| **Delete confirm** | Delete button hover | Red fill animation, 200ms |
| **Integrity banner** | Admin page load | Slide down from `-8px`, 350ms |
| **Gradient pulse** | Auth pages (optional) | Subtle scale oscillation (1.0 → 1.02 → 1.0) on mesh gradient, 8s infinite, very subtle |

---

## 13. Responsive Strategy

### 13.1 Breakpoints (from DESIGN.md)

| Name | Width | Key Changes |
|---|---|---|
| **Mobile** | < 600px | Nav collapses to logo + hamburger menu; 3-up metric grid → stacked; table → card layout; auth card full-width with reduced padding |
| **Tablet** | 600–959px | Nav horizontal; metric grid 2-up; table stays as table |
| **Desktop** | 960–1199px | Full 3-up metric grid; max-width 1000px container |
| **Wide** | ≥ 1200px | Admin max-width 1200px; dashboard stays at 1000px |

### 13.2 Touch Targets

All interactive elements must meet WCAG AAA 44×44px minimum:
- Buttons: `min-height: 44px`
- Nav links: `padding` inflated on mobile to meet 44px touch area
- Table action buttons: `padding: var(--space-xs) var(--space-sm)` minimum

### 13.3 Mobile Navigation

On < 600px:
- Nav bar shows logo + hamburger icon (3-bar SVG)
- Hamburger opens full-screen overlay: `background: var(--canvas)`, `z-index: 200`
- Overlay lists: Dashboard link, Admin link (if admin), Logout button
- Close button: `×` in top-right, 44×44px touch target

---

## 14. Accessibility Requirements

| Requirement | Implementation |
|---|---|
| **Skip link** | `<a href="#main-content" class="skip-link">Skip to main content</a>` in base.html, visible on `:focus-visible` |
| **Focus indicators** | `outline: 2px solid var(--link); outline-offset: 2px` on all interactive elements via `:focus-visible`. Never `outline: none` alone |
| **ARIA labels** | Tables: `aria-label="Your files"`. Banners: `role="status"` or `role="alert"`. Buttons: descriptive `aria-label` when icon-only |
| **Heading hierarchy** | Single `<h1>` per page. `<h2>` for sections. Never skip levels |
| **Color contrast** | `--ink` (#171717) on `--canvas` (#fff) = 15.4:1 ✓ AAA. `--body` (#4d4d4d) on `--canvas` = 7.8:1 ✓ AAA. `--mute` (#888) on `--canvas` = 3.5:1 ✓ AA for large text only — use for decorative labels only, never for essential content |
| **Reduced motion** | All animations wrapped in `@media (prefers-reduced-motion: no-preference)` |
| **Semantic HTML** | `<header>`, `<nav>`, `<main>`, `<footer>`, `<table>` with `<thead>/<tbody>`, `<form>` with `<label for="">` |
| **Form labels** | Every `<input>` must have an associated `<label>` with matching `for`/`id` attributes |

---

## 15. File Inventory & Change Map

### 15.1 Modified Files

| File | Action | Scope |
|---|---|---|
| `static/style.css` | **Full rewrite** | Replace 818 lines. Eliminate dark glassmorphism. Implement unified DESIGN.md token system |
| `templates/base.html` | **Rewrite** | New `<head>` with fonts + meta. Redesigned nav bar. Add footer. Dynamic `<title>` |
| `templates/login.html` | **Rewrite** | Mesh gradient backdrop + auth card from DESIGN.md |
| `templates/register.html` | **Rewrite** | Mirror login with extra username field |
| `templates/index.html` | **Rewrite** | New metric cards, enhanced upload dropzone, redesigned file table |
| `templates/admin.html` | **Minor update** | Remove `.admin-surface` scoping, use global tokens, add `{% block title %}` |
| `app.py` | **Add 2 error handlers** | `@app.errorhandler(403)` and `@app.errorhandler(404)` — 8 lines total |

### 15.2 New Files

| File | Description |
|---|---|
| `templates/403.html` | Custom forbidden page |
| `templates/404.html` | Custom not-found page |

### 15.3 Files NOT Changed

| File | Reason |
|---|---|
| `models.py` | No schema changes |
| `chain.py` | No blockchain logic changes |
| `config.py` | No config changes |
| `requirements.txt` | No new dependencies (all HTML/CSS) |

---

## 16. Verification Plan

### 16.1 Visual Verification

| Check | Method |
|---|---|
| All 5 pages render correctly | Manual browser walkthrough at `http://127.0.0.1:5000` |
| Light theme applied universally | No dark backgrounds (`#0f172a`) visible anywhere |
| Typography | Inter loaded for body, JetBrains Mono for code/hash elements |
| Responsive | Test at 375px (iPhone SE), 768px (iPad), 1440px (desktop) |
| Animations | Verify page-load fade, toast slide-in/out, button hover lift |
| Reduced motion | Toggle `prefers-reduced-motion: reduce` in DevTools — all animations should be instant |

### 16.2 Functional Verification

| Check | Method |
|---|---|
| Login flow | Register → Login → Dashboard → Logout — all functional |
| File operations | Upload → appears in table → Download → Delete — all functional |
| Admin access | Admin user sees 🛡 Admin button → Admin page loads with ledger |
| Non-admin block | Non-admin hitting `/admin` → Custom 403 page |
| 404 page | Hit `/nonexistent` → Custom 404 page |
| Flash messages | Upload success → green toast → auto-dismisses after 4s |
| File validation | Upload `.exe` → red toast "File type not allowed" |

### 16.3 Accessibility Verification

| Check | Method |
|---|---|
| Skip link | Tab on page load → "Skip to main content" link appears |
| Keyboard nav | Tab through all interactive elements — visible focus ring on each |
| Screen reader | Headings hierarchy correct, ARIA labels on tables/banners |
| Color contrast | Run axe-core or Lighthouse accessibility audit |

---

## 17. Out of Scope

| Item | Rationale |
|---|---|
| Dark mode toggle | Would require a second complete token set. Defer to v5.0 |
| JavaScript framework (React, Vue) | Project is Jinja + vanilla CSS/JS. No framework migration |
| Custom SVG icon system | Use emoji for now; SVG icon library (Lucide, Heroicons) is a future enhancement |
| File preview (image thumbnails) | Requires backend changes to generate thumbnails pre-encryption |
| Drag-and-drop upload (JS) | The `<input type="file">` wrapped in a dropzone is sufficient. Full JS drag-drop is an enhancement |
| Real-time notifications (WebSocket) | Out of scope for static Flask rendering |
| Progressive Web App (PWA) | No service worker or manifest required |
| Internationalization (i18n) | English only |
| CSRF tokens (Flask-WTF) | Deferred per PRD v3.0 §1.4 |

---

> **End of Spec**
>
> This document covers every UI surface, every component, every animation, and every token needed to execute the full overhaul. No backend logic changes are required beyond the 2 error handler registrations.
>
> **Estimated effort:** 4–6 hours of focused implementation.
