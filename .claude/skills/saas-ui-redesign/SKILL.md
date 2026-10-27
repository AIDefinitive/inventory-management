---
name: saas-ui-redesign
description: Redesign a Vue 3 application's UI into a modern SaaS-style interface - replaces a top navigation bar with a collapsible left vertical sidebar, introduces design tokens for consistent spacing/typography/color, and polishes cards, tables, forms, and page headers. Use when the user asks to modernize, restyle, or "make professional" a Vue 3 app's UI, move navigation to a sidebar, or apply a SaaS dashboard look. Preserves all existing functionality, routes, and data logic.
---

# SaaS UI Redesign for Vue 3

Transform an existing Vue 3 app into a polished SaaS-style interface:

- **Left vertical sidebar** replacing the top nav (collapsible, responsive).
- **Slim top bar** for page context and global controls (filters, locale, user menu).
- **Design tokens** (CSS custom properties) so spacing, type, color, radius, and shadow are consistent everywhere.
- **Consistent page patterns**: page header, cards, stat tiles, tables, buttons, forms, empty/loading/error states.

This is a **presentation-layer** change. Behavior must be identical before and after.

## Non-negotiable rules

1. **Do not change behavior.** No changes to API calls, stores/composables logic, routes/paths, props/emits contracts, or computed data. Only templates (structure/classes), styles, and new purely presentational layout components.
2. **No new dependencies** unless the user explicitly approves. Use inline SVG icons (see `references/layout-shell.md`), not an icon library.
3. **Respect project instructions.** Read the root `CLAUDE.md` and any `client/CLAUDE.md` first. If they require delegating `.vue` work to a specific subagent (for example `vue-expert`), do so and pass this skill's rules, tokens, and plan into the delegation prompt. Honor project design rules (palette, "no emojis", etc.); they override defaults here.
4. **Preserve i18n.** Every new user-visible string goes through the project's translation function and is added to **all** locale files.
5. **Accessibility is part of "polished."** Keyboard reachable, visible focus rings, `aria-current="page"` on the active nav item, labelled icon-only buttons, WCAG AA contrast.
6. **Comment non-obvious logic** (collapse persistence, breakpoint handling, focus management).
7. Work on a branch; never commit or push unless the user asks.

## Workflow

### Phase 1 - Discover (read-only)

Map the current UI before proposing anything:

- Entry and routing: `main.js`/`main.ts`, router config (route paths, names, meta).
- Root layout: `App.vue` - where the nav, header, global controls, and `<router-view>` live.
- Global styles: where base CSS lives (often `App.vue` `<style>` without `scoped`, or `src/assets/*.css`, `style.css`).
- Shared components rendered in the header (filters, locale switcher, profile menu, modals).
- i18n setup (`useI18n`, `vue-i18n`, locale files) and how nav labels are translated.
- Existing visual language: colors, fonts, recurring class names (`.card`, `.stat-card`, `.btn`, tables). `grep` for hard-coded hex colors and pixel paddings to gauge inconsistency.
- How the app is run and whether Playwright MCP tools are available for verification.

Produce a short inventory: nav items (label key, path, active-match rule), header controls, global style location, recurring patterns, and anything risky (very large views, scoped styles that override globals).

### Phase 2 - Plan and confirm

Present a concise plan and get the user's go-ahead (use AskUserQuestion when there are real choices):

- **Brand/accent color** - keep the project's existing palette by default; offer an accent if none exists.
- **Sidebar style** - dark (slate-900) or light (white with border). Default: dark, matching most SaaS dashboards.
- **Nav grouping** - flat list, or grouped sections (e.g. "Operations", "Finance", "Insights") if there are 6+ items.
- **Where global controls go** - default: filters stay at the top of the content area; locale + user menu move to the top bar (or sidebar footer if the user prefers).
- **Scope** - shell only (sidebar + top bar + tokens), or shell + per-page polish. Default: both, shell first.

### Phase 3 - Design tokens

Add the token layer from `references/design-tokens.css` to the global stylesheet, adapting colors to the project's palette. Then:

- Replace hard-coded values in **global** styles with tokens (`var(--space-4)`, `var(--color-text-muted)`, ...).
- Keep existing class names working (`.card`, `.stat-card`, etc.) - restyle them with tokens rather than renaming, so views keep working without template edits.
- Spacing comes only from the scale (4px base). No ad-hoc `13px` paddings.

### Phase 4 - Layout shell

Build the shell described in `references/layout-shell.md`:

- `components/layout/AppSidebar.vue` - brand, nav items with icons, active state, collapse toggle, optional footer.
- `components/layout/AppTopbar.vue` - current page title (from route meta or nav config), slot/area for global controls, mobile menu button.
- `App.vue` becomes a CSS Grid shell: `sidebar | (topbar / content)`.
- Nav items are defined once in a config array (label key, path, icon, exact-match flag) consumed by the sidebar - no duplicated markup.
- Collapse state persisted in `localStorage`; below the mobile breakpoint the sidebar becomes an off-canvas drawer with a backdrop, closes on route change and on `Escape`.
- Move existing header controls (filters, locale switcher, profile menu) into the new shell **without changing their internals**.

Verify the shell works on every route before touching individual pages.

### Phase 5 - Page polish

Apply the patterns in `references/layout-shell.md` ("Page patterns") view by view:

- Standard page header (title, description, right-aligned actions).
- Stat tiles in a responsive grid; cards with consistent padding, radius, border, and subtle shadow.
- Tables: sticky header where useful, comfortable row height, right-aligned numerics, tabular figures, hover state, horizontal scroll container on small screens.
- Buttons: primary / secondary / ghost / danger variants via shared classes; consistent heights.
- Forms and inputs: consistent height, focus ring, label spacing.
- Loading, empty, and error states use the same component/style everywhere.

Work one view at a time and keep diffs reviewable. For very large views, change classes and styles only; do not restructure logic.

**Parallelizing with subagents:** page polish splits well across agents if each owns a disjoint set of files and none edits the shared shell/global styles. But the Playwright MCP browser is a single shared session - parallel agents navigating and resizing it corrupt each other's screenshots and checks. Have parallel agents limit themselves to the build plus non-browser checks, and run Phase 6 browser verification once, sequentially, after all edits land.

### Phase 6 - Verify

Do not report success without evidence:

1. **Build** - run the project's build (e.g. `npm run build` / `npx vite build`) and fix any errors.
2. **Every route** - with Playwright MCP, visit each route; confirm it renders, the correct nav item is active, and the console has no *new* errors (note pre-existing ones separately).
3. **Responsive** - screenshot at 1440px, 1024px, and 390px wide. Check the sidebar collapsed/expanded states and the mobile drawer (open, close via backdrop, `Escape`, and route change).
4. **Interactions** - exercise filters, modals, menus, and any form submit to prove behavior is unchanged.
5. **Keyboard** - tab through the sidebar and top bar; focus is visible and order is logical.
6. **i18n** - switch every locale; no untranslated new strings, no layout breakage from longer labels.
7. **Tests** - run the project's existing test suite.

If the dev server does not pick up file changes (common on WSL with projects under `/mnt/c`), restart it with `CHOKIDAR_USEPOLLING=true` before verifying.

### Phase 7 - Report

Summarize: files added/changed, before/after screenshots (paths), what was verified and how, pre-existing issues noticed but not fixed, and any deviations from the plan. Offer to commit on a branch.

## Quality bar - "polished professional"

- One accent color, used sparingly (active nav, primary buttons, focus, key links).
- Neutral surfaces: page background slightly tinted (`--color-bg`), cards white, 1px borders (`--color-border`), at most a subtle shadow.
- Type: one sans-serif stack, 3-4 sizes in regular use, `font-variant-numeric: tabular-nums` for figures.
- Generous, consistent whitespace: `--space-6`/`--space-8` between sections, `--space-4`/`--space-5` inside cards.
- Alignment: page content max-width (e.g. 1440px) with consistent gutters; every page header sits on the same baseline.
- Motion: 150-200ms ease transitions on hover/collapse only; respect `prefers-reduced-motion`.
- No visual noise: no gradients on surfaces, no heavy shadows, no emojis, no decorative icons without meaning.
