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
    <div class="topbar-title">{{ title }}</div>
    <div class="topbar-actions">
      <slot />
    </div>
  </header>
</template>

<script>
import NavIcon from './NavIcon.vue'
import { useI18n } from '../../composables/useI18n'

export default {
  name: 'AppTopbar',
  components: { NavIcon },
  props: {
    title: { type: String, default: '' },
    mobileOpen: { type: Boolean, default: false }
  },
  emits: ['open-menu'],
  setup() {
    const { t } = useI18n()
    return { t }
  }
}
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
  flex-shrink: 0;
  padding: 0 var(--content-gutter);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}
/* A div, not h1: each view owns its page heading in .page-header */
.topbar-title {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  white-space: nowrap;
}
.topbar-actions { margin-left: auto; display: flex; align-items: center; gap: var(--space-3); }
.menu-button {
  display: none;
  place-items: center;
  width: 36px;
  height: 36px;
  border: 0;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--color-text);
  cursor: pointer;
}
.menu-button:hover { background: var(--color-surface-muted); }
/* Phone only; keep in sync with breakpoints.js */
@media (max-width: 639.98px) { .menu-button { display: grid; } }
/* Phones: the page's own heading repeats the title, so drop it to keep the controls on one row */
@media (max-width: 480px) {
  .topbar { gap: var(--space-2); }
  .topbar-title { display: none; }
}
</style>
