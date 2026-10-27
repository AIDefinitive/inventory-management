<template>
  <div :class="['app-shell', `mode-${mode}`, { 'sidebar-collapsed': iconsOnly }]">
    <AppSidebar
      :collapsed="iconsOnly"
      :mobile-open="mobileOpen"
      :mode="mode"
      :overlay="overlayOpen"
      @toggle-collapse="toggleCollapsed"
    />
    <div v-if="mobileOpen || overlayOpen" class="sidebar-backdrop" @click="closeTransient" />

    <div class="app-main">
      <AppTopbar :title="pageTitle" :mobile-open="mobileOpen" @open-menu="mobileOpen = true">
        <LanguageSwitcher />
        <ProfileMenu
          @show-profile-details="showProfileDetails = true"
          @show-tasks="showTasks = true"
        />
      </AppTopbar>
      <FilterBar />
      <main class="app-content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'
import AppSidebar from './components/layout/AppSidebar.vue'
import AppTopbar from './components/layout/AppTopbar.vue'
import { findNavItem } from './components/layout/navItems'
import { PHONE_QUERY, WIDE_QUERY } from './components/layout/breakpoints'

export default {
  name: 'App',
  components: {
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher,
    AppSidebar,
    AppTopbar
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const route = useRoute()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    // Three modes, driven by matchMedia (see layout/breakpoints.js):
    //   phone   (<640)      off-canvas drawer, labels always shown
    //   compact (640-1279)  icons-only rail; expanding is a temporary overlay
    //   wide    (>=1280)    expanded by default; manual collapse is persisted
    const STORAGE_KEY = 'sidebar-collapsed'
    const phoneQuery = window.matchMedia(PHONE_QUERY)
    const wideQuery = window.matchMedia(WIDE_QUERY)
    const computeMode = () => (phoneQuery.matches ? 'phone' : wideQuery.matches ? 'wide' : 'compact')
    // Initialised synchronously so the first paint already has the right layout.
    const mode = ref(computeMode())

    // Wide-mode preference; only the wide toggle ever writes it.
    const collapsed = ref(localStorage.getItem(STORAGE_KEY) === 'true')
    // Compact overlay and phone drawer are temporary and never persisted.
    const overlayOpen = ref(false)
    const mobileOpen = ref(false)

    // Visible icons-only state: wide uses the stored preference, compact is a
    // rail unless the overlay is open, phone drawer always shows labels.
    const iconsOnly = computed(() => {
      if (mode.value === 'wide') return collapsed.value
      if (mode.value === 'compact') return !overlayOpen.value
      return false
    })

    const toggleCollapsed = () => {
      if (mode.value === 'wide') {
        collapsed.value = !collapsed.value
        localStorage.setItem(STORAGE_KEY, String(collapsed.value))
      } else if (mode.value === 'compact') {
        overlayOpen.value = !overlayOpen.value
      }
    }

    const closeTransient = () => {
      mobileOpen.value = false
      overlayOpen.value = false
    }

    const onBreakpoint = () => {
      mode.value = computeMode()
      // Any mode change drops transient state so it can't reappear later.
      closeTransient()
    }

    // Navigating closes the drawer/overlay; Escape too.
    watch(() => route.fullPath, closeTransient)
    const onKeydown = (e) => { if (e.key === 'Escape') closeTransient() }

    const pageTitle = computed(() => {
      const item = findNavItem(route.path)
      return item ? t(item.labelKey) : ''
    })

    onMounted(() => {
      loadTasks()
      phoneQuery.addEventListener('change', onBreakpoint)
      wideQuery.addEventListener('change', onBreakpoint)
      window.addEventListener('keydown', onKeydown)
    })
    onBeforeUnmount(() => {
      phoneQuery.removeEventListener('change', onBreakpoint)
      wideQuery.removeEventListener('change', onBreakpoint)
      window.removeEventListener('keydown', onKeydown)
    })

    return {
      t,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask,
      mode,
      iconsOnly,
      overlayOpen,
      toggleCollapsed,
      closeTransient,
      mobileOpen,
      pageTitle
    }
  }
}
</script>

<style>
/* Kept: views rely on the zero-margin reset for headings, paragraphs and lists. */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* ---- Shell ---- */
.app-shell {
  display: grid;
  grid-template-columns: auto 1fr;
  min-height: 100vh;
}

.app-main {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.app-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--space-8) var(--content-gutter);
}

.sidebar-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  z-index: var(--z-backdrop);
}

/* Compact: the rail is out of flow (fixed) so it can grow into an overlay;
   this column reserves its collapsed width and the content never reflows. */
.app-shell.mode-compact { grid-template-columns: var(--sidebar-width-collapsed) minmax(0, 1fr); }
.app-shell.mode-compact .app-main { grid-column: 2; }

/* Phone: sidebar is an off-canvas drawer. Keep in sync with breakpoints.js */
@media (max-width: 639.98px) {
  .app-shell { grid-template-columns: minmax(0, 1fr); }
}

/* ---- Page header ---- */
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
  margin-bottom: var(--space-6);
}

.page-header h2 {
  font-size: var(--text-xl);
  font-weight: var(--weight-semibold);
  line-height: var(--leading-tight);
  color: var(--color-text);
}

.page-header p {
  margin-top: var(--space-1);
  color: var(--color-text-muted);
}

/* ---- Stat tiles ---- */
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
  box-shadow: var(--shadow-sm);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.stat-card:hover {
  border-color: var(--color-border-strong);
  box-shadow: var(--shadow-md);
}

.stat-label {
  margin-bottom: var(--space-2);
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: var(--weight-semibold);
  line-height: var(--leading-tight);
  color: var(--color-text);
}

/* Color semantics preserved from the previous design */
.stat-card.warning .stat-value { color: var(--color-warning); }
.stat-card.success .stat-value { color: var(--color-success); }
.stat-card.danger .stat-value { color: var(--color-danger); }
.stat-card.info .stat-value { color: var(--color-info); }

/* ---- Cards ---- */
.card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: var(--space-5);
  margin-bottom: var(--space-6);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  line-height: var(--leading-tight);
  color: var(--color-text);
}

/* ---- Tables ---- */
.table-container { overflow-x: auto; }

table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

thead { background: var(--color-surface-muted); }

th {
  text-align: left;
  padding: var(--space-3);
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

td {
  padding: var(--space-3);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
  font-variant-numeric: tabular-nums;
}

tbody tr { transition: background-color var(--transition-fast); }
tbody tr:hover { background: var(--color-surface-muted); }
tbody tr:last-child td { border-bottom: 0; }

/* ---- Badges ---- */
.badge {
  display: inline-flex;
  align-items: center;
  height: 22px;
  padding: 0 var(--space-2);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--weight-medium);
  white-space: nowrap;
  background: var(--color-surface-muted);
  color: var(--color-text-muted);
}

.badge.success,
.badge.increasing {
  background: var(--color-success-soft);
  color: var(--color-success);
}

.badge.info,
.badge.low,
.badge.stable {
  background: var(--color-info-soft);
  color: var(--color-info);
}

.badge.warning,
.badge.medium {
  background: var(--color-warning-soft);
  color: var(--color-warning);
}

.badge.danger,
.badge.decreasing,
.badge.high {
  background: var(--color-danger-soft);
  color: var(--color-danger);
}

/* ---- Buttons ---- */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  height: var(--control-height);
  padding: 0 var(--space-4);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  font: inherit;
  font-weight: var(--weight-medium);
  cursor: pointer;
  transition: background var(--transition-fast), border-color var(--transition-fast), color var(--transition-fast);
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: var(--color-accent); color: #fff; }
.btn-primary:hover:not(:disabled) { background: var(--color-accent-hover); }
.btn-secondary {
  background: var(--color-surface);
  color: var(--color-text);
  border-color: var(--color-border-strong);
}
.btn-secondary:hover:not(:disabled) { background: var(--color-surface-muted); }
.btn-ghost { background: transparent; color: var(--color-text-muted); }
.btn-ghost:hover:not(:disabled) { background: var(--color-surface-muted); color: var(--color-text); }
.btn-danger { background: var(--color-danger); color: #fff; }
.btn-danger:hover:not(:disabled) { background: #b91c1c; }

/* ---- Loading / empty / error ---- */
.loading,
.empty-state {
  padding: var(--space-10) var(--space-6);
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

.empty-state {
  border: 1px dashed var(--color-border-strong);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
}

.error {
  margin: var(--space-4) 0;
  padding: var(--space-4);
  border: 1px solid var(--color-danger);
  border-radius: var(--radius-md);
  background: var(--color-danger-soft);
  color: var(--color-danger);
  font-size: var(--text-sm);
}
</style>
