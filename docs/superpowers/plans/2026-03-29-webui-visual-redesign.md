# WebUI Visual Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign all 4 WebUI pages (Chat, Config, Skills, Team) + shared layout to a modern minimalist dark theme, using pure CSS + HTML changes only.

**Architecture:** Rewrite `style.css` with new design tokens, then update each template's inline `<style>` to use new variables. Replace emoji with inline SVG icons. Add subtle transitions and polish. No new dependencies, no backend changes.

**Tech Stack:** Plain CSS with CSS custom properties, vanilla JS (unchanged), Jinja2 templates (HTML structure only changes), inline SVG icons.

---

### Task 1: Rewrite style.css — New Design System

**Files:**
- Rewrite: `nanobot/webui/static/css/style.css`

This task replaces the entire CSS file with the new design system. All subsequent tasks depend on this.

- [ ] **Step 1: Write the complete new style.css**

Replace `nanobot/webui/static/css/style.css` with the new design system:

```css
/* ─── Design System ─────────────────────────────────────────────── */

:root {
  /* Background layers */
  --bg-base: #09090b;
  --bg-surface: #18181b;
  --bg-elevated: #27272a;
  --bg-hover: #3f3f46;

  /* Text layers */
  --text-primary: #fafafa;
  --text-secondary: #a1a1aa;
  --text-tertiary: #71717a;

  /* Accent */
  --accent-primary: #6366f1;
  --accent-secondary: #8b5cf6;
  --accent-gradient: linear-gradient(135deg, #6366f1, #8b5cf6);

  /* Semantic colors */
  --color-success: #22c55e;
  --color-error: #ef4444;
  --color-warning: #f59e0b;
  --color-info: #3b82f6;

  /* Borders */
  --border-default: #27272a;
  --border-hover: #3f3f46;
  --border-focus: #6366f1;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.4);
  --shadow-glow: 0 0 0 2px rgba(99, 102, 241, 0.25);

  /* Spacing */
  --sp-1: 0.25rem;
  --sp-2: 0.5rem;
  --sp-3: 0.75rem;
  --sp-4: 1rem;
  --sp-5: 1.5rem;
  --sp-6: 2rem;
  --sp-8: 3rem;

  /* Radius */
  --radius-sm: 0.375rem;
  --radius-md: 0.625rem;
  --radius-lg: 1rem;
  --radius-full: 9999px;

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 200ms ease;

  /* Typography */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  --font-mono: 'SF Mono', 'Cascadia Code', 'Fira Code', Consolas, monospace;
}

/* ─── Reset ──────────────────────────────────────────────────────── */

*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: var(--font-sans);
  background: var(--bg-base);
  color: var(--text-primary);
  line-height: 1.6;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a { color: var(--accent-primary); text-decoration: none; }
a:hover { text-decoration: underline; }

/* ─── Navigation ─────────────────────────────────────────────────── */

.nav {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 var(--sp-5);
  background: rgba(9, 9, 11, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-default);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
  text-decoration: none;
  letter-spacing: -0.01em;
}

.nav-brand:hover { text-decoration: none; }

.nav-brand svg {
  width: 22px;
  height: 22px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: var(--sp-1);
  list-style: none;
}

.nav-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  padding: var(--sp-2) var(--sp-3);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: var(--radius-sm);
  transition: color var(--transition-fast), background var(--transition-fast);
}

.nav-link:hover {
  color: var(--text-primary);
  background: var(--bg-elevated);
  text-decoration: none;
}

.nav-link.active {
  color: var(--text-primary);
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: var(--sp-3);
  right: var(--sp-3);
  height: 2px;
  background: var(--accent-gradient);
  border-radius: 1px;
}

.nav-link svg {
  width: 16px;
  height: 16px;
  opacity: 0.7;
}

.nav-link:hover svg,
.nav-link.active svg { opacity: 1; }

.nav-logout-btn {
  padding: var(--sp-1) var(--sp-3);
  background: transparent;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  color: var(--text-tertiary);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-left: var(--sp-2);
}

.nav-logout-btn:hover {
  color: var(--text-primary);
  border-color: var(--border-hover);
  background: var(--bg-elevated);
}

/* ─── Main content ───────────────────────────────────────────────── */

.main {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--sp-5);
}

/* ─── Cards ──────────────────────────────────────────────────────── */

.card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: var(--sp-5);
  transition: border-color var(--transition-normal);
}

.card:hover { border-color: var(--border-hover); }

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--sp-4);
  padding-bottom: var(--sp-3);
  border-bottom: 1px solid var(--border-default);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.card-subtitle {
  font-size: 0.8125rem;
  color: var(--text-tertiary);
}

.card-subsection {
  margin-bottom: var(--sp-5);
  padding: var(--sp-4);
  background: var(--bg-base);
  border-radius: var(--radius-sm);
}

/* ─── Buttons ────────────────────────────────────────────────────── */

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--sp-2);
  padding: var(--sp-2) var(--sp-4);
  font-size: 0.875rem;
  font-weight: 500;
  border-radius: var(--radius-sm);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-sans);
  line-height: 1.4;
}

.btn-primary {
  background: var(--accent-gradient);
  color: white;
  border: none;
}

.btn-primary:hover {
  filter: brightness(1.1);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-primary:active { transform: translateY(0); }

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
  filter: none;
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-default);
}

.btn-ghost:hover {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border-color: var(--border-hover);
}

.btn-danger {
  background: transparent;
  color: var(--color-error);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: var(--color-error);
}

/* Legacy aliases for existing templates */
.form-btn {
  padding: var(--sp-2) var(--sp-4);
  border-radius: var(--radius-sm);
  border: none;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-sans);
}
.form-btn { background: var(--accent-gradient); color: white; }
.form-btn:hover { filter: brightness(1.1); }
.form-btn:active { transform: translateY(1px); }
.form-btn-secondary { background: var(--bg-elevated); color: var(--text-primary); border: 1px solid var(--border-default); }
.form-btn-secondary:hover { background: var(--bg-hover); }

/* ─── Form inputs ────────────────────────────────────────────────── */

.form-group { margin-bottom: var(--sp-4); }

.form-label {
  display: block;
  margin-bottom: var(--sp-1);
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 500;
}

.form-input,
.config-field-input,
.modal-field-input,
.modal-field-select,
.skill-name-input {
  width: 100%;
  padding: var(--sp-2) var(--sp-3);
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 0.875rem;
  font-family: var(--font-sans);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.form-input:focus,
.config-field-input:focus,
.modal-field-input:focus,
.modal-field-select:focus,
.skill-name-input:focus {
  outline: none;
  border-color: var(--border-focus);
  box-shadow: var(--shadow-glow);
}

.form-input::placeholder,
.config-field-input::placeholder { color: var(--text-tertiary); }

.form-textarea { min-height: 120px; resize: vertical; }

/* ─── Tables ─────────────────────────────────────────────────────── */

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th, .table td {
  padding: var(--sp-3) var(--sp-4);
  text-align: left;
  border-bottom: 1px solid var(--border-default);
}

.table th {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.table tr:hover td { background: var(--bg-surface); }
.table tr:last-child td { border-bottom: none; }

/* ─── Badges ─────────────────────────────────────────────────────── */

.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: var(--radius-full);
  letter-spacing: 0.02em;
}

.badge-admin {
  background: rgba(99, 102, 241, 0.15);
  color: var(--accent-primary);
}

.badge-member {
  background: rgba(161, 161, 170, 0.15);
  color: var(--text-secondary);
}

/* ─── Code blocks ────────────────────────────────────────────────── */

pre {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: var(--sp-4);
  overflow-x: auto;
  margin: var(--sp-3) 0;
}

code {
  font-family: var(--font-mono);
  font-size: 0.8125rem;
  color: var(--text-primary);
}

/* ─── Modals (shared) ────────────────────────────────────────────── */

.modal {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 1000;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.modal.active {
  display: flex;
  animation: modalFadeIn var(--transition-normal) forwards;
}

@keyframes modalFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--sp-6);
  width: 100%;
  max-width: 480px;
  box-shadow: var(--shadow-md);
  animation: modalSlideUp 300ms ease forwards;
}

@keyframes modalSlideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--sp-4);
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: var(--text-tertiary);
  cursor: pointer;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.modal-close:hover {
  color: var(--text-primary);
  background: var(--bg-elevated);
}

.modal-body { margin-bottom: var(--sp-5); }
.modal-footer { display: flex; justify-content: flex-end; gap: var(--sp-2); }

.modal-field { margin-bottom: var(--sp-4); }

.modal-field-label {
  display: block;
  margin-bottom: var(--sp-1);
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.modal-actions {
  display: flex;
  gap: var(--sp-2);
  justify-content: flex-end;
  margin-top: var(--sp-5);
}

.modal-btn {
  padding: var(--sp-2) var(--sp-4);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-sans);
}

.modal-btn-cancel {
  background: var(--bg-elevated);
  border: 1px solid var(--border-default);
  color: var(--text-secondary);
}
.modal-btn-cancel:hover { background: var(--bg-hover); color: var(--text-primary); }

.modal-btn-primary {
  background: var(--accent-gradient);
  border: none;
  color: white;
}
.modal-btn-primary:hover { filter: brightness(1.1); }

/* ─── Status messages (shared) ──────────────────────────────────── */

.status-message {
  padding: var(--sp-2) var(--sp-3);
  border-radius: var(--radius-sm);
  margin-bottom: var(--sp-4);
  font-size: 0.8125rem;
  display: none;
}

.status-message.success {
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: var(--color-success);
  display: block;
}

.status-message.error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: var(--color-error);
  display: block;
}

/* ─── Login page ─────────────────────────────────────────────────── */

.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: var(--bg-base);
}

.login-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--sp-8);
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.login-card h2 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: var(--sp-5);
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-card p {
  color: var(--text-secondary);
  font-size: 0.875rem;
  line-height: 1.6;
}

.login-card code {
  background: var(--bg-elevated);
  padding: var(--sp-1) var(--sp-2);
  border-radius: var(--radius-sm);
  font-size: 0.8125rem;
}

.login-error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: var(--color-error);
  padding: var(--sp-2);
  border-radius: var(--radius-sm);
  font-size: 0.8125rem;
  margin-top: var(--sp-4);
}

/* ─── Layout ─────────────────────────────────────────────────────── */

.layout {
  display: flex;
  min-height: calc(100vh - 56px);
}

.sidebar {
  width: 250px;
  background: var(--bg-surface);
  border-right: 1px solid var(--border-default);
  padding: var(--sp-4);
  overflow-y: auto;
}

.content {
  flex: 1;
  padding: var(--sp-5);
  overflow-y: auto;
}

/* ─── Responsive ─────────────────────────────────────────────────── */

@media (max-width: 768px) {
  .nav-links { display: none; }
  .layout { flex-direction: column; }
  .sidebar {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--border-default);
  }
}

/* ─── Utility classes ────────────────────────────────────────────── */

.text-center { text-align: center; }
.text-right { text-align: right; }
.hidden { display: none !important; }
.flex { display: flex; }
.flex-col { flex-direction: column; }
.items-center { align-items: center; }
.justify-between { justify-content: space-between; }
.justify-center { justify-content: center; }
.gap-2 { gap: var(--sp-2); }
.gap-3 { gap: var(--sp-3); }
.gap-4 { gap: var(--sp-4); }
.w-full { width: 100%; }
.select-none { user-select: none; }

/* ─── Legacy compatibility ───────────────────────────────────────── */
/* Keep old variable names as aliases so existing inline styles work */

:root {
  --bg-primary: var(--bg-base);
  --bg-secondary: var(--bg-surface);
  --bg-tertiary: var(--bg-elevated);
  --text-muted: var(--text-tertiary);
  --accent: var(--accent-primary);
  --accent-hover: #4f46e5;
  --border-color: var(--border-default);
  --border-hover: var(--border-hover);
  --success: var(--color-success);
  --error: var(--color-error);
  --warning: var(--color-warning);
  --info: var(--color-info);
  --spacing-xs: var(--sp-1);
  --spacing-sm: var(--sp-2);
  --spacing-md: var(--sp-4);
  --spacing-lg: var(--sp-5);
  --spacing-xl: var(--sp-6);
}
```

- [ ] **Step 2: Commit**

```bash
git add nanobot/webui/static/css/style.css
git commit -m "style: rewrite CSS design system with new dark minimalist theme"
```

---

### Task 2: Redesign base.html — Navigation + SVG Icons

**Files:**
- Rewrite: `nanobot/webui/templates/base.html`

- [ ] **Step 1: Replace base.html with redesigned navigation**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}nanobot{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="https://unpkg.com/htmx.org@2.0.4"></script>
    {% block head %}{% endblock %}
</head>
<body>
    <nav class="nav">
        <a href="/chat" class="nav-brand">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 5c.67 0 1.35.09 2 .26 1.78-2.17 4.76-2.87 7.2-1.7.97.47 1.54 1.5 1.54 2.58 0 1.31-.87 2.46-2.12 2.85.24.84.38 1.73.38 2.66 0 4.42-4.03 8-9 8s-9-3.58-9-8 4.03-8 9-8z"/>
                <circle cx="9" cy="13" r="1" fill="currentColor"/>
                <circle cx="15" cy="13" r="1" fill="currentColor"/>
            </svg>
            nanobot
        </a>
        <div class="nav-links">
            <a href="/chat" class="nav-link {% block nav_chat %}{% endblock %}">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                Chat
            </a>
            <a href="/config" class="nav-link {% block nav_config %}{% endblock %}">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                Config
            </a>
            <a href="/skills" class="nav-link {% block nav_skills %}{% endblock %}">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>
                Skills
            </a>
            <a href="/team" class="nav-link {% block nav_team %}{% endblock %}">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                Team
            </a>
            <form action="/api/auth/logout" method="post" style="display:inline">
                <button type="submit" class="nav-logout-btn">Logout</button>
            </form>
        </div>
    </nav>
    <main class="main">
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add nanobot/webui/templates/base.html
git commit -m "style: redesign navigation with SVG icons and glassmorphism"
```

---

### Task 3: Redesign login.html

**Files:**
- Rewrite: `nanobot/webui/templates/login.html`

- [ ] **Step 1: Replace login.html with gradient logo design**

```html
{% extends "base.html" %}
{% block title %}Login - nanobot{% endblock %}

{% block content %}
<div class="login-container">
    <div class="login-card">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="url(#grad)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: var(--sp-4);">
            <defs><linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#6366f1"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient></defs>
            <path d="M12 5c.67 0 1.35.09 2 .26 1.78-2.17 4.76-2.87 7.2-1.7.97.47 1.54 1.5 1.54 2.58 0 1.31-.87 2.46-2.12 2.85.24.84.38 1.73.38 2.66 0 4.42-4.03 8-9 8s-9-3.58-9-8 4.03-8 9-8z"/>
            <circle cx="9" cy="13" r="1" fill="url(#grad)"/>
            <circle cx="15" cy="13" r="1" fill="url(#grad)"/>
        </svg>
        <h2>nanobot WebUI</h2>
        <p>Run <code>nanobot webui</code> in your terminal to get a login URL.</p>
        {% if error %}
        <p class="login-error">{{ error }}</p>
        {% endif %}
    </div>
</div>
{% endblock %}
```

- [ ] **Step 2: Commit**

```bash
git add nanobot/webui/templates/login.html
git commit -m "style: redesign login page with gradient logo"
```

---

### Task 4: Redesign chat.html — Message Bubbles + Input

**Files:**
- Rewrite: `nanobot/webui/templates/chat.html`

This is the most complex page. The `<style>` block gets new variables + restyled components. The JS logic stays identical — only CSS classes and HTML structure change for the visual elements.

Key changes:
- **User messages**: gradient background (`var(--accent-gradient)`), right-aligned, rounded with sharp bottom-right
- **AI messages**: `var(--bg-surface)` background with 3px left accent border, rounded with sharp bottom-left
- **Progress indicator**: collapsible card with animated spinner
- **Input area**: textarea with internal send button, glow on focus
- **Active nav**: add `{% block nav_chat %}active{% endblock %}`

The JS code (lines 289-595) is **NOT modified** — only the `<style>` block and HTML structure change.

- [ ] **Step 1: Replace the entire `<style>` block inside `{% block head %}` with new chat styles**

The new `<style>` block replaces all existing chat CSS. Key differences:
- Message bubbles use `.msg-user` / `.msg-assistant` with new accent gradient
- Input wrapper uses `position: relative` with absolute send button
- Sidebar items use `border-left: 2px solid transparent` → accent on active
- Empty state uses SVG instead of emoji

- [ ] **Step 2: Add `active` class to chat nav link**

In the template, ensure `{% block nav_chat %}active{% endblock %}` is set (add via the extends block).

- [ ] **Step 3: Replace emoji empty state with SVG**

Change the empty state `<div class="empty-state-icon">💬</div>` to an SVG chat bubble icon.

- [ ] **Step 4: Commit**

```bash
git add nanobot/webui/templates/chat.html
git commit -m "style: redesign chat page with gradient message bubbles"
```

---

### Task 5: Redesign config.html — Section Tabs + Form Polish

**Files:**
- Rewrite: `nanobot/webui/templates/config.html`

Key changes:
- **Sidebar nav**: rounded items with left accent border on active (no full accent fill)
- **Form fields**: label font changes to `0.75rem uppercase tracking-wide` secondary color
- **Save button**: gradient with hover lift effect
- **Restart banner**: subtle amber left-border instead of full background
- **Active nav**: add `{% block nav_config %}active{% endblock %}`

The JS code (lines 492-650) is **NOT modified**.

- [ ] **Step 1: Replace the `<style>` block with new config styles**

- [ ] **Step 2: Add active class to config nav**

- [ ] **Step 3: Commit**

```bash
git add nanobot/webui/templates/config.html
git commit -m "style: redesign config page with polished form controls"
```

---

### Task 6: Redesign skills.html — Card Editor + Modals

**Files:**
- Rewrite: `nanobot/webui/templates/skills.html`

Key changes:
- **Skill list items**: border-left accent, no full accent fill on active
- **Editor textarea**: monospace with subtle line number feel (padding-left gutter)
- **Modals**: use shared modal styles from style.css + slide-up animation
- **Import area**: dashed border with gradient on drag-over
- **Active nav**: add `{% block nav_skills %}active{% endblock %}`

The JS code (lines 391-652) is **NOT modified**.

- [ ] **Step 1: Replace the `<style>` block with new skills styles**

- [ ] **Step 2: Add active class to skills nav**

- [ ] **Step 3: Commit**

```bash
git add nanobot/webui/templates/skills.html
git commit -m "style: redesign skills page with card editor"
```

---

### Task 7: Redesign team.html — Card Grid + Member Cards

**Files:**
- Rewrite: `nanobot/webui/templates/team.html`

Key changes:
- **Layout**: Replace `<table>` with CSS Grid of member cards (`grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`)
- **Member cards**: each shows avatar circle (first letter), nickname, role badge, channel pills
- **Action buttons**: visible on card hover, hidden by default
- **Modals**: use shared styles from style.css
- **Active nav**: add `{% block nav_team %}active{% endblock %}`

The JS requires minor changes to `renderMembers()` to output card HTML instead of table rows.

- [ ] **Step 1: Replace the `<style>` block with card-grid styles**

- [ ] **Step 2: Replace the `<table>` in HTML with a `<div class="team-grid" id="membersGrid">` container**

- [ ] **Step 3: Update `renderMembers()` JS function to output card HTML instead of table rows**

Each card:
```html
<div class="member-card">
  <div class="member-avatar">A</div>
  <div class="member-name">alice</div>
  <div class="badge badge-admin">admin</div>
  <div class="member-channels">
    <span class="channel-pill">telegram: 123</span>
  </div>
  <div class="member-actions">
    <button class="btn btn-ghost" onclick="openEditModal('alice')">Edit</button>
    <button class="btn btn-danger" onclick="removeMember('alice')">Remove</button>
  </div>
</div>
```

- [ ] **Step 4: Add active class to team nav**

- [ ] **Step 5: Commit**

```bash
git add nanobot/webui/templates/team.html
git commit -m "style: redesign team page with member card grid"
```

---

### Task 8: Visual Smoke Test + Final Polish

**Files:**
- Possibly tweak: `nanobot/webui/static/css/style.css` or any template

- [ ] **Step 1: Run the existing WebUI tests**

```bash
pytest tests/test_webui_integration.py tests/test_webui_auth.py -v --tb=short
```

Expected: All pass. Templates must still render correctly (Jinja2 blocks not broken).

- [ ] **Step 2: Review each page visually by starting the gateway**

```bash
nanobot gateway &
nanobot webui
```

Check: Login page gradient, nav active states, chat bubbles, config form focus glow, skills editor, team card grid.

- [ ] **Step 3: Fix any visual inconsistencies found**

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "style: final polish for WebUI visual redesign"
```
