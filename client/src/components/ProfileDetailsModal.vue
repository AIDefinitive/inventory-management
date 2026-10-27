<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click="close">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">{{ t('profileDetails.title') }}</h3>
            <button class="close-button" @click="close">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="profile-section">
              <div class="avatar-section">
                <div class="avatar-xl">
                  {{ getInitials(currentUser.name) }}
                </div>
                <h4 class="profile-name">{{ currentUser.name }}</h4>
                <p class="profile-job-title">{{ currentUser.jobTitle }}</p>
              </div>

              <div class="info-grid">
                <div class="info-item">
                  <div class="info-label">{{ t('profileDetails.email') }}</div>
                  <div class="info-value">{{ currentUser.email }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">{{ t('profileDetails.department') }}</div>
                  <div class="info-value">{{ currentUser.department }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">{{ t('profileDetails.location') }}</div>
                  <div class="info-value">{{ currentUser.location }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">{{ t('profileDetails.phone') }}</div>
                  <div class="info-value">{{ currentUser.phone }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">{{ t('profileDetails.joinDate') }}</div>
                  <div class="info-value">{{ formatDate(currentUser.joinDate) }}</div>
                </div>

                <div class="info-item">
                  <div class="info-label">{{ t('profileDetails.employeeId') }}</div>
                  <div class="info-value">CC-{{ currentUser.id.toString().padStart(5, '0') }}</div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn btn-secondary" @click="close">{{ t('profileDetails.close') }}</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { useAuth } from '../composables/useAuth'
import { useI18n } from '../composables/useI18n'

const { currentUser, getInitials } = useAuth()
const { t, currentLocale } = useI18n()

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
  return date.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
/* Overlay: slate tint; fixed z-index token keeps it above sticky bars and dropdowns */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: var(--space-4);
}

.modal-container {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  font-size: var(--text-lg);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  margin: 0;
}

.close-button {
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  width: var(--control-height);
  height: var(--control-height);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  transition: background var(--transition-fast), color var(--transition-fast);
}
.close-button:hover { background: var(--color-surface-muted); color: var(--color-text); }

.modal-body { flex: 1; overflow-y: auto; padding: var(--space-6); }

.modal-footer {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

/* Modal transitions */
.modal-enter-active, .modal-leave-active { transition: opacity var(--transition-base); }
.modal-enter-active .modal-container, .modal-leave-active .modal-container { transition: transform var(--transition-base); }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-container, .modal-leave-to .modal-container { transform: scale(0.97); }

@media (max-width: 639px) {
  .modal-header { padding: var(--space-3) var(--space-4); }
  .modal-body { padding: var(--space-4); }
  .modal-footer { padding: var(--space-3) var(--space-4); }
}

.profile-section { display: flex; flex-direction: column; gap: var(--space-6); }

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.avatar-xl {
  width: 80px;
  height: 80px;
  border-radius: var(--radius-full);
  background: var(--color-accent);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--weight-semibold);
  font-size: var(--text-xl);
  letter-spacing: 0.025em;
}

.profile-name { font-size: var(--text-xl); font-weight: var(--weight-semibold); color: var(--color-text); margin: 0; }
.profile-job-title { font-size: var(--text-base); color: var(--color-text-muted); margin: 0; }

/* min() lets the grid collapse to one column inside narrow phone modals */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
  gap: var(--space-5) var(--space-6);
}

.info-item { display: flex; flex-direction: column; gap: var(--space-1); min-width: 0; }
.info-label {
  font-size: var(--text-xs);
  font-weight: var(--weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-muted);
}
.info-value { font-size: var(--text-sm); color: var(--color-text); font-weight: var(--weight-medium); overflow-wrap: anywhere; }
</style>
