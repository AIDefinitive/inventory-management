<template>
  <aside
    id="app-sidebar"
    :class="['sidebar', { collapsed, overlay, compact: mode === 'compact', 'mobile-open': mobileOpen }]"
    :aria-label="t('nav.mainNavigation')"
  >
    <div class="sidebar-brand">
      <div class="brand-mark" aria-hidden="true">{{ brandInitial }}</div>
      <div v-if="!collapsed" class="brand-text">
        <span class="brand-name">{{ t('nav.companyName') }}</span>
        <span class="brand-subtitle">{{ t('nav.subtitle') }}</span>
      </div>
    </div>

    <nav class="sidebar-nav" :aria-label="t('nav.mainNavigation')">
      <div v-for="section in navSections" :key="section.labelKey || 'main'" class="nav-section">
        <div v-if="section.labelKey && !collapsed" class="nav-section-label">{{ t(section.labelKey) }}</div>
        <router-link
          v-for="item in section.items"
          :key="item.path"
          :to="item.path"
          :class="['nav-item', { active: isActive(item) }]"
          :aria-current="isActive(item) ? 'page' : undefined"
          :aria-label="collapsed ? t(item.labelKey) : undefined"
        >
          <NavIcon :name="item.icon" />
          <span v-if="!collapsed" class="nav-label">{{ t(item.labelKey) }}</span>
          <!-- Icons-only tooltip: decorative, the link's aria-label carries the name -->
          <span v-else class="nav-tooltip" aria-hidden="true">{{ t(item.labelKey) }}</span>
        </router-link>
      </div>
    </nav>

    <div class="sidebar-footer">
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

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavIcon from './NavIcon.vue'
import { navSections, isNavItemActive } from './navItems'
import { useI18n } from '../../composables/useI18n'

export default {
  name: 'AppSidebar',
  components: { NavIcon },
  props: {
    collapsed: { type: Boolean, default: false },
    mobileOpen: { type: Boolean, default: false },
    // 'wide' | 'compact' | 'phone'
    mode: { type: String, default: 'wide' },
    // Compact mode only: expanded as a temporary overlay above the content
    overlay: { type: Boolean, default: false }
  },
  emits: ['toggle-collapse'],
  setup() {
    const route = useRoute()
    const { t } = useI18n()
    const brandInitial = computed(() => t('nav.companyName').charAt(0).toUpperCase())
    const isActive = (item) => isNavItemActive(item, route.path)
    return { t, navSections, isActive, brandInitial }
  }
}
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
}
.sidebar.collapsed { width: var(--sidebar-width-collapsed); }

/* Compact: fixed rail so it can widen over the content without reflowing it.
   App.vue reserves the collapsed width in the grid. */
.sidebar.compact { position: fixed; left: 0; top: 0; }
.sidebar.compact.overlay { z-index: var(--z-drawer); box-shadow: var(--shadow-lg); }

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  height: var(--topbar-height);
  flex-shrink: 0;
  padding: 0 var(--space-5);
  border-bottom: 1px solid var(--sidebar-hover-bg);
}
.collapsed .sidebar-brand { padding: 0; justify-content: center; }
.brand-mark {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: var(--color-accent);
  color: #fff;
  display: grid;
  place-items: center;
  font-weight: var(--weight-semibold);
  flex-shrink: 0;
}
.brand-text { display: flex; flex-direction: column; min-width: 0; line-height: var(--leading-tight); }
.brand-name {
  color: #fff;
  font-weight: var(--weight-semibold);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.brand-subtitle {
  font-size: var(--text-xs);
  color: var(--sidebar-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Brand text is ellipsised, so no sidebar-level clipping is needed (tooltips and focus rings must escape). */
.sidebar-nav { flex: 1; overflow-y: auto; overflow-x: hidden; padding: var(--space-4) var(--space-3); }
/* Icons-only: nothing to scroll horizontally and tooltips must escape the nav box */
.collapsed .sidebar-nav { overflow: visible; }
.nav-section + .nav-section { margin-top: var(--space-6); }
/* Headings are hidden when icons-only; a divider keeps the grouping visible */
.collapsed .nav-section + .nav-section {
  margin-top: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--sidebar-hover-bg);
}
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
  top: 8px;
  bottom: 8px;
  width: 3px;
  border-radius: 0 3px 3px 0;
  background: var(--sidebar-active-indicator);
}
/* Sidebar is dark; keep the ring inside the item box */
.nav-item:focus-visible,
.collapse-toggle:focus-visible { outline-offset: -2px; }

/* CSS tooltip to the right of the icon (icons-only state) */
.nav-tooltip {
  position: absolute;
  left: calc(100% + var(--space-3));
  top: 50%;
  transform: translateY(-50%);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  background: #0f172a;
  color: #fff;
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  visibility: hidden;
  z-index: var(--z-modal);
  box-shadow: var(--shadow-md);
  transition: opacity var(--transition-fast), visibility var(--transition-fast);
}
.nav-item:hover .nav-tooltip,
.nav-item:focus-visible .nav-tooltip { opacity: 1; visibility: visible; }
@media (prefers-reduced-motion: reduce) {
  .nav-tooltip { transition: none; }
}

.sidebar-footer {
  padding: var(--space-3);
  border-top: 1px solid var(--sidebar-hover-bg);
}
.collapse-toggle {
  display: grid;
  place-items: center;
  width: 100%;
  height: 36px;
  border: 0;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--sidebar-text-muted);
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast);
}
.collapse-toggle:hover { background: var(--sidebar-hover-bg); color: var(--sidebar-active-text); }

/* Phone only (keep in sync with breakpoints.js): off-canvas drawer; collapse mode does not apply */
@media (max-width: 639.98px) {
  .sidebar,
  .sidebar.collapsed {
    position: fixed;
    left: 0;
    top: 0;
    width: var(--sidebar-width);
    transform: translateX(-100%);
    transition: transform var(--transition-base);
    z-index: var(--z-drawer);
  }
  .sidebar.mobile-open { transform: translateX(0); box-shadow: var(--shadow-lg); }
  .collapse-toggle { display: none; }
}
</style>
