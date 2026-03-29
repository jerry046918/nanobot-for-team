# WebUI Visual Redesign Spec

## Overview

Full visual redesign of the nanobot WebUI dashboard (Chat, Config, Skills, Team pages). Modern minimalist dark theme inspired by ChatGPT/Claude. Pure CSS + HTML template changes only — no new dependencies, no frameworks, all existing functionality preserved.

## Design System (Design Tokens)

### Color Palette

Three-layer depth system for backgrounds, text, and accents.

**Backgrounds (dark → light):**
- `--bg-base`: `#09090b` — page background
- `--bg-surface`: `#18181b` — cards, sidebar, input areas
- `--bg-elevated`: `#27272a` — hover states, dropdowns, borders
- `--bg-hover`: `#3f3f46` — active/hover highlights

**Text (light → muted):**
- `--text-primary`: `#fafafa` — headings, primary content
- `--text-secondary`: `#a1a1aa` — descriptions, secondary info
- `--text-tertiary`: `#71717a` — timestamps, placeholders, hints

**Accent:**
- `--accent-primary`: `#6366f1` — primary actions (indigo)
- `--accent-secondary`: `#8b5cf6` — gradients, secondary accent (violet)
- `--accent-gradient`: `linear-gradient(135deg, #6366f1, #8b5cf6)` — buttons, highlights

**Semantic:**
- `--color-success`: `#22c55e`
- `--color-error`: `#ef4444`
- `--color-warning`: `#f59e0b`
- `--color-info`: `#3b82f6`

**Borders:**
- `--border-default`: `#27272a`
- `--border-focus`: `#6366f1`

### Typography

- Font family: `-apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif`
- Monospace: `'SF Mono', 'Cascadia Code', 'Fira Code', Consolas, monospace`
- Scale: 0.75rem / 0.8125rem / 0.875rem / 1rem / 1.125rem / 1.25rem / 1.5rem
- Line heights: 1.4 (body), 1.6 (reading text)

### Spacing

Based on 4px grid: `0.25rem` / `0.5rem` / `0.75rem` / `1rem` / `1.5rem` / `2rem` / `3rem`

### Border Radius

- `--radius-sm`: `0.375rem` — inputs, badges
- `--radius-md`: `0.625rem` — cards, modals
- `--radius-lg`: `1rem` — large containers
- `--radius-full`: `9999px` — pills, avatars

### Shadows

Minimal approach:
- `--shadow-sm`: `0 1px 2px rgba(0,0,0,0.3)` — subtle elevation
- `--shadow-md`: `0 4px 12px rgba(0,0,0,0.4)` — modals, popovers
- `--shadow-glow`: `0 0 0 2px rgba(99,102,241,0.3)` — focus rings

### Transitions

- Default: `200ms ease` — hover, focus, color changes
- Layout: `300ms ease` — sidebar collapse, modal enter
- `--transition-fast`: `150ms ease`
- `--transition-normal`: `200ms ease`

---

## Component Library

### Buttons

Two variants:

**Primary (gradient):**
- Background: `var(--accent-gradient)`
- Text: white
- Hover: brightness +10%, subtle scale(1.01)
- Disabled: opacity 0.5, no pointer

**Ghost (transparent):**
- Background: transparent
- Border: 1px `var(--border-default)`
- Text: `var(--text-secondary)`
- Hover: background `var(--bg-hover)`, text `var(--text-primary)`

**Size variants:** sm (padding 4px 12px), md (8px 16px), lg (10px 24px)

### Form Inputs

- Background: `var(--bg-surface)`
- Border: 1px `var(--border-default)`
- Border-radius: `var(--radius-sm)`
- Focus: border `var(--border-focus)` + `var(--shadow-glow)`
- Placeholder: `var(--text-tertiary)`

### Cards

- Background: `var(--bg-surface)`
- Border: 1px `var(--border-default)`
- Border-radius: `var(--radius-md)`
- Hover: border `var(--bg-elevated)`, subtle `var(--shadow-sm)`
- Padding: `1.25rem`

### Modals

- Backdrop: `rgba(0,0,0,0.6)` with `backdrop-filter: blur(4px)`
- Container: `var(--bg-surface)` centered, max-width 480px
- Enter animation: fade-in + slide-up (transform translateY(20px) → 0)
- Border-radius: `var(--radius-lg)`

### Toast Notifications

- Position: top-right, stacked
- Background: `var(--bg-elevated)`
- Border-left: 3px semantic color
- Auto-dismiss: 3s with progress bar animation
- Enter: slide-in from right

### Badges

- Small pills with `var(--radius-full)`
- Role badges: admin = indigo, member = zinc
- Source badges: workspace = green, built-in = zinc

---

## Page Designs

### Navigation Bar

```
┌─────────────────────────────────────────────────────┐
│ ◈ nanobot          Chat  Config  Skills  Team  [⏏] │
│ (logo+text)        ───── (active underline)          │
└─────────────────────────────────────────────────────┘
```

- Fixed top, `backdrop-filter: blur(12px)` + semi-transparent `var(--bg-base)`
- Bottom border: 1px `var(--border-default)`
- Logo: small SVG icon + "nanobot" text, `var(--text-primary)`
- Nav links: `var(--text-secondary)`, hover → `var(--text-primary)`
- Active link: bottom 2px `var(--accent-primary)` indicator
- Logout: icon button, right-aligned

### Chat Page

```
┌──────────┬──────────────────────────────────┐
│ Sessions │        Message Area               │
│          │                                    │
│ [Today]  │  AI ○─────────────────────────     │
│  session1│     │ AI message text here with    │
│  session2│     │ nice left-border accent      │
│          │  ○─────────────────────────────    │
│ [Older]  │                                    │
│  session3│        ──── User message ────      │
│          │     (right-aligned, gradient bg)   │
│          │                                    │
│          │  ○ Tool: web_search               │
│          │    └─ 3 results found             │
│          │                                    │
│          ├──────────────────────────────────┤
│          │  [Type a message...        ] [➤] │
└──────────┴──────────────────────────────────┘
```

**Left sidebar (260px):**
- Header: "Sessions" + search icon
- Session list: clickable items with title + timestamp
- Active session: `var(--bg-elevated)` background + left 2px accent border
- Hover: `var(--bg-hover)` background

**Message area:**
- User messages: right-aligned, `var(--accent-gradient)` background, white text, `var(--radius-md)` with bottom-right sharper
- AI messages: left-aligned, `var(--bg-surface)` background, 3px left border `var(--accent-primary)`, `var(--radius-md)` with bottom-left sharper
- Tool progress: collapsible card, monospace tool name, subtle animated spinner

**Input area:**
- Full-width textarea with `var(--bg-surface)` background
- Send button: gradient circle icon, right-aligned inside input
- Focus: `var(--shadow-glow)` around textarea

### Config Page

```
┌──────────┬──────────────────────────────────┐
│ Sections │        Form Area                  │
│          │                                    │
│ ◉ Agents │  ┌── Agents ──────────────────┐  │
│   Providers│  │                            │  │
│   Channels │  │  Workspace Path           │  │
│   Tools    │  │  [________________________]│  │
│   Gateway  │  │                            │  │
│   Team     │  │  Model                    │  │
│   WebUI    │  │  [________________________]│  │
│           │  │                            │  │
│           │  │  Provider                 │  │
│           │  │  [dropdown___________ ▾]  │  │
│           │  └────────────────────────────┘  │
│           │                                    │
│           │         [Save Changes]             │
└──────────┴──────────────────────────────────┘
```

**Left sidebar (200px):**
- Section list with icons (SVG), text labels
- Active: `var(--bg-elevated)` background + left accent border

**Form area:**
- Grouped in fieldsets with title + description
- Labels: `var(--text-secondary)`, small uppercase tracking
- Inputs: full-width with description text below
- Sections toggled via JS (same as current, restyled)

**Save button:** fixed bottom-right, gradient, with loading state

### Skills Page

```
┌──────────┬──────────────────────────────────┐
│ Skills   │        Editor                     │
│          │                                    │
│ [+ New]  │  ┌── SKILL.md ─────────────────┐  │
│          │  │  Name: [my-skill________]     │  │
│ 👤 skill1│  │                                │  │
│ 🔧 skill2│  │  ┌──────────────────────────┐ │  │
│ 👤 skill3│  │  │ # My Skill              │ │  │
│          │  │  │                          │ │  │
│          │  │  │ Skill content here...    │ │  │
│          │  │  └──────────────────────────┘ │  │
│          │  │                                │  │
│          │  │  [Save]  [Delete]              │  │
│          │  └────────────────────────────────┘  │
└──────────┴──────────────────────────────────┘
```

**Left sidebar (240px):**
- "New Skill" button at top
- Skill cards: name + source badge (workspace/built-in)
- Active: `var(--bg-elevated)` + left accent border

**Editor:**
- Name input (disabled when editing existing)
- Content textarea: monospace font, line-height 1.6
- Toolbar: Save (primary) + Delete (ghost) buttons
- Import ZIP: drag-drop area with dashed border

### Team Page

```
┌──────────────────────────────────────────────┐
│ Team Members                    [+ Add Member]│
│                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ A        │  │ B        │  │ C        │   │
│  │ alice    │  │ bob      │  │ charlie  │   │
│  │ [admin]  │  │ [member] │  │ [member] │   │
│  │ tg slack │  │ discord  │  │ feishu   │   │
│  │    [⋯]   │  │    [⋯]   │  │    [⋯]   │   │
│  └──────────┘  └──────────┘  └──────────┘   │
│                                               │
└──────────────────────────────────────────────┘
```

**Card-based layout** (replacing table):
- Grid of member cards (responsive: 3 cols → 2 → 1)
- Each card: avatar circle (first letter), nickname, role badge, channel binding pills
- Hover: reveal action buttons (edit, remove)
- Add member: opens modal with form

---

## Responsive Design

- **Desktop (>1024px):** Full two-column layouts
- **Tablet (768-1024px):** Sidebar collapses to icon-only or overlay
- **Mobile (<768px):** Single column, hamburger menu for navigation

## Accessibility

- All interactive elements have visible focus rings (`var(--shadow-glow)`)
- Color contrast ratio ≥ 4.5:1 for all text
- SVG icons include `aria-label` attributes
- Modals trap focus and support Escape to close
- Form inputs have associated labels

## Files to Modify

| File | Change Type |
|------|------------|
| `nanobot/webui/static/css/style.css` | Complete rewrite with new design system |
| `nanobot/webui/templates/base.html` | New navigation, SVG icons, design tokens |
| `nanobot/webui/templates/login.html` | Redesigned login with centered card |
| `nanobot/webui/templates/chat.html` | Restyled messages, input, sidebar |
| `nanobot/webui/templates/config.html` | Restyled sidebar, forms, sections |
| `nanobot/webui/templates/skills.html` | Restyled editor, cards, modals |
| `nanobot/webui/templates/team.html` | Card grid layout, member cards, modals |

No new files. No new dependencies. No backend changes.

## Implementation Order

1. `style.css` — Design system tokens + all component styles
2. `base.html` — Navigation + shared structure
3. `login.html` — Login page
4. `chat.html` — Chat (most complex, highest priority)
5. `config.html` — Configuration
6. `skills.html` — Skills editor
7. `team.html` — Team management
