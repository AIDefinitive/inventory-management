# Layout Shell and Page Patterns

Reference implementations for Phase 4 (shell) and Phase 5 (page polish). Adapt to the project:

- Swap `t(...)` for the project's i18n function (`useI18n()` from the project's composable or `vue-i18n`). If the app has no i18n, use plain strings.
- Match the project's script style (`<script setup>` vs `setup()` return), JS vs TS.
- Move the project's existing header controls into the marked slots; do not rewrite them.

## 1. Nav config - `src/components/layout/navItems.js`

Define nav once; the sidebar and top bar both read it.

```js
// Each item: label i18n key, route path, icon name (see icons below).
// `exact` makes "/" active only on the home route instead of on every route.
export const navSections = [
  {
    labelKey: null, // null = no section heading
    items: [
      { labelKey: 'nav.overview', path: '/', icon: 'home', exact: true },
      { labelKey: 'nav.inventory', path: '/inventory', icon: 'box' },
      { labelKey: 'nav.orders', path: '/orders', icon: 'clipboard' }
    ]
  }
  // Add more sections ({ labelKey: 'nav.sections.finance', items: [...] }) for 6+ items.
]

export const isNavItemActive = (item, currentPath) =>
  item.exact ? currentPath === item.path : currentPath === item.path || currentPath.startsWith(item.path + '/')

export const findNavItem = (currentPath) =>
  navSections.flatMap((s) => s.items).find((item) => isNavItemActive(item, currentPath))
```

## 2. Icons - `src/components/layout/NavIcon.vue`

Inline SVG, 20px, `currentColor`, stroke style. No icon library.

```vue
<template>
  <svg class="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none"
       stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"
       aria-hidden="true">
    <path v-for="d in paths" :key="d" :d="d" />
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ name: { type: String, required: true } })

// Minimal Lucide-style path set. Extend as needed; unknown names render a dot.
const ICONS = {
  home: ['M3 10.5 12 3l9 7.5', 'M5 9.5V21h14V9.5'],
  box: ['M21 8 12 3 3 8l9 5 9-5Z', 'M3 8v8l9 5 9-5V8', 'M12 13v8'],
  clipboard: ['M9 4h6v3H9z', 'M9 5H6v16h12V5h-3', 'M9 12h6', 'M9 16h4'],
  chart: ['M4 20V10', 'M10 20V4', 'M16 20v-7', 'M22 20H2'],
  trending: ['M3 17l6-6 4 4 8-8', 'M15 7h6v6'],
  wallet: ['M3 7h16a2 2 0 0 1 2 2v10H3z', 'M3 7V5h14v2', 'M16 13h2'],
  truck: ['M3 6h11v10H3z', 'M14 10h4l3 3v3h-7', 'M7 19a2 2 0 1 0 0-.01', 'M17 19a2 2 0 1 0 0-.01'],
  file: ['M6 3h8l4 4v14H6z', 'M14 3v4h4', 'M9 13h6', 'M9 17h6'],
  settings: ['M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z', 'M19 12h2M3 12h2M12 3v2M12 19v2M17 7l1.5-1.5M5.5 18.5 7 17M17 17l1.5 1.5M5.5 5.5 7 7'],
  menu: ['M4 6h16', 'M4 12h16', 'M4 18h16'],
  chevronLeft: ['M15 18l-6-6 6-6'],
  chevronRight: ['M9 18l6-6-6-6'],
  close: ['M6 6l12 12', 'M18 6 6 18']
}

const paths = computed(() => ICONS[props.name] || ['M12 12h.01'])
</script>

<style scoped>
.nav-icon { flex-shrink: 0; display: block; }
</style>
```

## 3. Sidebar - `src/components/layout/AppSidebar.vue`

```vue
<template>
  <aside
    id="app-sidebar"
    :class="['sidebar', { collapsed, 'mobile-open': mobileOpen }]"
    :aria-label="t('nav.mainNavigation')"
  >
    <div class="sidebar-brand">
      <div class="brand-mark" aria-hidden="true">{{ brandInitial }}</div>
      <span v-if="!collapsed" class="brand-name">{{ brandName }}</span>
    </div>

    <nav class="sidebar-nav">
      <div v-for="section in navSections" :key="section.labelKey || 'main'" class="nav-section">
        <div v-if="section.labelKey && !collapsed" class="nav-section-label">{{ t(section.labelKey) }}</div>
        <router-link
          v-for="item in section.items"
          :key="item.path"
          :to="item.path"
          :class="['nav-item', { active: isNavItemActive(item, route.path) }]"
          :aria-current="isNavItemActive(item, route.path) ? 'page' : undefined"
          :title="collapsed ? t(item.labelKey) : undefined"
        >
          <NavIcon :name="item.icon" />
          <span v-if="!collapsed" class="nav-label">{{ t(item.labelKey) }}</span>
        </router-link>
      </div>
    </nav>

    <div class="sidebar-footer">
      <slot name="footer" />
      <button
        type="button"
        class="collapse-toggle"
        :aria-label="collapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')"
        :aria-expanded="!collapsed"
        aria-controls="app-sidebar"
        @click="$emit('toggle-collapse')"
      >
        <NavIcon :name="collapsed ? 'chevronRight' : 'chevronLeft'" />
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavIcon from './NavIcon.vue'
import { navSections, isNavItemActive } from './navItems'
// import { useI18n } from '<project i18n composable>'

const props = defineProps({
  collapsed: { type: Boolean, default: false },
  mobileOpen: { type: Boolean, default: false },
  brandName: { type: String, required: true }
})
defineEmits(['toggle-collapse'])

const route = useRoute()
// const { t } = useI18n()
const brandInitial = computed(() => props.brandName.charAt(0).toUpperCase())
</script>

<style scoped>
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  width: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
  transition: width var(--transition-base);
  z-index: var(--z-sidebar);
  overflow: hidden;
}
.sidebar.collapsed { width: var(--sidebar-width-collapsed); }

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: var(--topbar-height);
  padding: 0 var(--space-5);
  border-bottom: 1px solid var(--sidebar-hover-bg);
}
.brand-mark {
  width: 28px; height: 28px;
  border-radius: var(--radius-sm);
  background: var(--color-accent);
  color: #fff;
  display: grid; place-items: center;
  font-weight: var(--weight-semibold);
  flex-shrink: 0;
}
.brand-name { color: #fff; font-weight: var(--weight-semibold); white-space: nowrap; }

.sidebar-nav { flex: 1; overflow-y: auto; padding: var(--space-4) var(--space-3); }
.nav-section + .nav-section { margin-top: var(--space-6); }
.nav-section-label {
  padding: 0 var(--space-3) var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--sidebar-text-muted);
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: 40px;
  padding: 0 var(--space-3);
  margin-bottom: var(--space-1);
  border-radius: var(--radius-md);
  color: var(--sidebar-text);
  text-decoration: none;
  font-weight: var(--weight-medium);
  white-space: nowrap;
  transition: background var(--transition-fast), color var(--transition-fast);
}
.collapsed .nav-item { justify-content: center; padding: 0; }
.nav-item:hover { background: var(--sidebar-hover-bg); color: var(--sidebar-active-text); }
.nav-item.active { background: var(--sidebar-active-bg); color: var(--sidebar-active-text); }
/* Accent bar marks the active page without relying on color alone */
.nav-item.active::before {
  content: '';
  position: absolute;
  left: calc(-1 * var(--space-3));
  top: 8px; bottom: 8px;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: var(--sidebar-active-indicator);
}

.sidebar-footer {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-3);
  border-top: 1px solid var(--sidebar-hover-bg);
}
.collapse-toggle {
  display: grid; place-items: center;
  height: 36px;
  border: 0;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--sidebar-text-muted);
  cursor: pointer;
}
.collapse-toggle:hover { background: var(--sidebar-hover-bg); color: var(--sidebar-active-text); }

/* Mobile: off-canvas drawer; the collapse toggle is irrelevant there */
@media (max-width: 1024px) {
  .sidebar,
  .sidebar.collapsed {
    position: fixed;
    left: 0; top: 0;
    width: var(--sidebar-width);
    transform: translateX(-100%);
    transition: transform var(--transition-base);
    z-index: var(--z-drawer);
  }
  .sidebar.mobile-open { transform: translateX(0); box-shadow: var(--shadow-lg); }
  .collapse-toggle { display: none; }
}
</style>
```

When `collapsed` is true on mobile, still render labels: pass `:collapsed="collapsed && !isMobile"` from the shell.

## 4. Top bar - `src/components/layout/AppTopbar.vue`

```vue
<template>
  <header class="topbar">
    <button
      type="button"
      class="menu-button"
      :aria-label="t('nav.openMenu')"
      aria-controls="app-sidebar"
      :aria-expanded="mobileOpen"
      @click="$emit('open-menu')"
    >
      <NavIcon name="menu" />
    </button>
    <h1 class="topbar-title">{{ title }}</h1>
    <div class="topbar-actions">
      <!-- Existing global controls go here unchanged: locale switcher, profile menu, etc. -->
      <slot />
    </div>
  </header>
</template>

<script setup>
import NavIcon from './NavIcon.vue'
defineProps({ title: { type: String, default: '' }, mobileOpen: { type: Boolean, default: false } })
defineEmits(['open-menu'])
// const { t } = useI18n()
</script>

<style scoped>
.topbar {
  position: sticky;
  top: 0;
  z-index: calc(var(--z-sidebar) - 1);
  display: flex;
  align-items: center;
  gap: var(--space-4);
  height: var(--topbar-height);
  padding: 0 var(--content-gutter);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}
.topbar-title { margin: 0; font-size: var(--text-lg); font-weight: var(--weight-semibold); }
.topbar-actions { margin-left: auto; display: flex; align-items: center; gap: var(--space-3); }
.menu-button {
  display: none;
  border: 0; background: transparent; color: var(--color-text);
  width: 36px; height: 36px; border-radius: var(--radius-md); cursor: pointer;
  place-items: center;
}
.menu-button:hover { background: var(--color-surface-muted); }
@media (max-width: 1024px) { .menu-button { display: grid; } }
</style>
```

## 5. Shell - `App.vue`

```vue
<template>
  <div :class="['app-shell', { 'sidebar-collapsed': effectiveCollapsed }]">
    <AppSidebar
      :collapsed="effectiveCollapsed"
      :mobile-open="mobileOpen"
      :brand-name="t('app.brandName')"
      @toggle-collapse="toggleCollapsed"
    />
    <div v-if="mobileOpen" class="sidebar-backdrop" @click="mobileOpen = false" />

    <div class="app-main">
      <AppTopbar :title="pageTitle" :mobile-open="mobileOpen" @open-menu="mobileOpen = true">
        <!-- existing LanguageSwitcher / ProfileMenu / etc. moved here unchanged -->
      </AppTopbar>
      <!-- existing global filter bar (if any) can sit here, above the content -->
      <main class="app-content">
        <router-view />
      </main>
    </div>
    <!-- existing global modals stay at the end, unchanged -->
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from './components/layout/AppSidebar.vue'
import AppTopbar from './components/layout/AppTopbar.vue'
import { findNavItem } from './components/layout/navItems'

const route = useRoute()
// const { t } = useI18n()

// Desktop collapse preference survives reloads.
const STORAGE_KEY = 'sidebar-collapsed'
const collapsed = ref(localStorage.getItem(STORAGE_KEY) === 'true')
const toggleCollapsed = () => {
  collapsed.value = !collapsed.value
  localStorage.setItem(STORAGE_KEY, String(collapsed.value))
}

// Track the mobile breakpoint so the drawer, not the collapse mode, applies on small screens.
const mobileQuery = window.matchMedia('(max-width: 1024px)')
const isMobile = ref(mobileQuery.matches)
const onBreakpoint = (e) => { isMobile.value = e.matches; if (!e.matches) mobileOpen.value = false }
const effectiveCollapsed = computed(() => collapsed.value && !isMobile.value)

const mobileOpen = ref(false)
// Navigating from the drawer should close it.
watch(() => route.fullPath, () => { mobileOpen.value = false })
const onKeydown = (e) => { if (e.key === 'Escape') mobileOpen.value = false }

onMounted(() => {
  mobileQuery.addEventListener('change', onBreakpoint)
  window.addEventListener('keydown', onKeydown)
})
onBeforeUnmount(() => {
  mobileQuery.removeEventListener('change', onBreakpoint)
  window.removeEventListener('keydown', onKeydown)
})

const pageTitle = computed(() => {
  const item = findNavItem(route.path)
  return item ? t(item.labelKey) : ''
})
</script>

<style>
/* Global (unscoped): tokens + base styles from design-tokens.css live here or in a global css file. */
.app-shell {
  display: grid;
  grid-template-columns: auto 1fr;
  min-height: 100vh;
}
.app-main { min-width: 0; display: flex; flex-direction: column; }
.app-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--space-8) var(--content-gutter) var(--space-12);
}
.sidebar-backdrop {
  position: fixed; inset: 0;
  background: rgba(15, 23, 42, 0.45);
  z-index: var(--z-backdrop);
}
@media (max-width: 1024px) {
  .app-shell { grid-template-columns: 1fr; }
}
</style>
```

## Page patterns

Restyle the project's existing class names with these rules so views improve without template rewrites. Only add markup where a pattern is missing (e.g. a page with no header).

```css
/* Page header */
.page-header {
  display: flex; align-items: flex-end; justify-content: space-between;
  gap: var(--space-4); flex-wrap: wrap;
  margin-bottom: var(--space-6);
}
.page-header h2 { margin: 0; font-size: var(--text-xl); font-weight: var(--weight-semibold); line-height: var(--leading-tight); }
.page-header p { margin: var(--space-1) 0 0; color: var(--color-text-muted); }

/* Cards */
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--space-5);
}
.card + .card { margin-top: var(--space-6); }
.card-header {
  display: flex; align-items: center; justify-content: space-between;
  gap: var(--space-3); margin-bottom: var(--space-4);
}
.card-title { margin: 0; font-size: var(--text-lg); font-weight: var(--weight-semibold); }

/* Stat tiles */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}
.stat-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
}
.stat-label { font-size: var(--text-xs); font-weight: var(--weight-medium); color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 0.04em; }
.stat-value { margin-top: var(--space-2); font-size: var(--text-2xl); font-weight: var(--weight-semibold); }

/* Tables */
.table-container { overflow-x: auto; margin: 0 calc(-1 * var(--space-5)); }
table { width: 100%; border-collapse: collapse; font-size: var(--text-sm); }
th {
  text-align: left; padding: var(--space-3) var(--space-5);
  font-size: var(--text-xs); font-weight: var(--weight-semibold);
  text-transform: uppercase; letter-spacing: 0.04em;
  color: var(--color-text-muted); background: var(--color-surface-muted);
  border-bottom: 1px solid var(--color-border);
}
td { padding: var(--space-3) var(--space-5); border-bottom: 1px solid var(--color-border); }
tbody tr:hover { background: var(--color-surface-muted); }
tbody tr:last-child td { border-bottom: 0; }
th.num, td.num { text-align: right; font-variant-numeric: tabular-nums; }

/* Buttons */
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: var(--space-2);
  height: var(--control-height); padding: 0 var(--space-4);
  border-radius: var(--radius-md); border: 1px solid transparent;
  font: inherit; font-weight: var(--weight-medium); cursor: pointer;
  transition: background var(--transition-fast), border-color var(--transition-fast);
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--color-accent); color: #fff; }
.btn-primary:hover:not(:disabled) { background: var(--color-accent-hover); }
.btn-secondary { background: var(--color-surface); color: var(--color-text); border-color: var(--color-border-strong); }
.btn-secondary:hover:not(:disabled) { background: var(--color-surface-muted); }
.btn-ghost { background: transparent; color: var(--color-text-muted); }
.btn-ghost:hover:not(:disabled) { background: var(--color-surface-muted); color: var(--color-text); }
.btn-danger { background: var(--color-danger); color: #fff; }

/* Inputs */
input:not([type=checkbox]):not([type=radio]):not([type=range]), select, textarea {
  height: var(--control-height); padding: 0 var(--space-3);
  border: 1px solid var(--color-border-strong); border-radius: var(--radius-md);
  background: var(--color-surface); color: var(--color-text); font: inherit;
}
textarea { height: auto; padding: var(--space-2) var(--space-3); }
input:focus-visible, select:focus-visible, textarea:focus-visible {
  outline: none; border-color: var(--color-focus);
  box-shadow: 0 0 0 3px var(--color-accent-soft);
}

/* Badges (status) */
.badge {
  display: inline-flex; align-items: center; height: 22px; padding: 0 var(--space-2);
  border-radius: var(--radius-full); font-size: var(--text-xs); font-weight: var(--weight-medium);
}
.badge.success { background: var(--color-success-soft); color: var(--color-success); }
.badge.info    { background: var(--color-info-soft);    color: var(--color-info); }
.badge.warning { background: var(--color-warning-soft); color: var(--color-warning); }
.badge.danger  { background: var(--color-danger-soft);  color: var(--color-danger); }

/* Loading / empty / error */
.loading, .empty-state, .error {
  padding: var(--space-10) var(--space-6);
  text-align: center; color: var(--color-text-muted);
  border: 1px dashed var(--color-border-strong); border-radius: var(--radius-lg);
  background: var(--color-surface);
}
.error { color: var(--color-danger); border-color: var(--color-danger); background: var(--color-danger-soft); }
```

## New i18n keys the shell needs

Add to every locale: `nav.mainNavigation`, `nav.collapseSidebar`, `nav.expandSidebar`, `nav.openMenu`, `app.brandName` (or reuse the existing brand key), and any `nav.sections.*` headings used.
