<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="initialLoading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="loadError && !recommendation" class="error">{{ loadError }}</div>
    <div v-else>
      <div class="card budget-card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budget') }}</h3>
          <span class="budget-value">{{ money(budget) }}</span>
        </div>
        <input
          type="range"
          class="budget-slider"
          min="0"
          :max="sliderMax"
          :step="SLIDER_STEP"
          v-model.number="budget"
          :aria-label="t('restocking.budgetSlider')"
          :disabled="sliderMax === 0"
        />
        <div class="slider-scale">
          <span>{{ money(0) }}</span>
          <span>{{ t('restocking.fullRestockCost', { amount: money(fullRestockCost) }) }}</span>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.budget') }}</div>
          <div class="stat-value">{{ money(budget) }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.recommendedTotal') }}</div>
          <div class="stat-value">{{ money(totalCost) }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('restocking.remainingBudget') }}</div>
          <div class="stat-value">{{ money(remainingBudget) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.itemsAndUnits') }}</div>
          <div class="stat-value">{{ items.length }} / {{ totalUnits }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.recommendations') }} ({{ items.length }})</h3>
          <button
            type="button"
            class="btn btn-primary"
            :disabled="!canPlaceOrder"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.placing') : t('restocking.placeOrder') }}
          </button>
        </div>

        <div v-if="loadError" class="error">{{ loadError }}</div>
        <div v-if="orderError" class="error" role="alert">{{ orderError }}</div>
        <div v-if="placedOrder" class="success-message" role="status">
          <span>{{ t('restocking.orderSuccess', { orderNumber: placedOrder.order_number, date: formatDate(placedOrder.expected_delivery) }) }}</span>
          <router-link to="/orders" class="view-orders-link">{{ t('restocking.viewOrders') }}</router-link>
        </div>

        <div v-if="items.length === 0" class="empty-state">
          <p class="empty-title">{{ fullRestockCost === 0 ? t('restocking.nothingToRestock') : t('restocking.emptyTitle') }}</p>
          <p v-if="fullRestockCost > 0">{{ t('restocking.emptyHint') }}</p>
        </div>
        <div v-else class="table-container" :class="{ stale: pending }">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th class="num">{{ t('restocking.table.demandGap') }}</th>
                <th class="num">{{ t('restocking.table.recommendedQty') }}</th>
                <th class="num">{{ t('restocking.table.unitCost') }}</th>
                <th class="num">{{ t('restocking.table.lineTotal') }}</th>
                <th class="num">{{ t('restocking.table.leadTime') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in items" :key="item.item_sku">
                <td><strong>{{ item.item_sku }}</strong></td>
                <td>{{ translateProductName(item.item_name) }}</td>
                <td>
                  <span :class="['badge', item.trend]">{{ trendLabel(item.trend) }}</span>
                </td>
                <td class="num">{{ item.demand_gap.toLocaleString() }}</td>
                <td class="num"><strong>{{ item.recommended_quantity.toLocaleString() }}</strong></td>
                <td class="num">{{ money(item.unit_cost, 2) }}</td>
                <td class="num"><strong>{{ money(item.line_total, 2) }}</strong></td>
                <td class="num">{{ item.lead_time_days }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrencyWithDecimals } from '../utils/currency'

const { t, currentLocale, currentCurrency, translateProductName } = useI18n()

const SLIDER_STEP = 10
const DEBOUNCE_MS = 250

const initialLoading = ref(true)
const loadError = ref(null)
const recommendation = ref(null) // raw API response
const budget = ref(0)
const pending = ref(false) // a debounced/in-flight fetch exists for the current slider value
const submitting = ref(false)
const orderError = ref(null)
const placedOrder = ref(null)
const fullRestockCost = ref(0)

// Slider max: full restock cost rounded UP to the next step so the top of the
// slider always covers every gap (e.g. 4000.08 -> 4010).
const sliderMax = computed(() => Math.ceil(fullRestockCost.value / SLIDER_STEP) * SLIDER_STEP)

const items = computed(() => recommendation.value?.items ?? [])
const totalCost = computed(() => recommendation.value?.total_cost ?? 0)
const remainingBudget = computed(() => recommendation.value?.remaining_budget ?? budget.value)
const totalUnits = computed(() => items.value.reduce((sum, i) => sum + i.recommended_quantity, 0))
const canPlaceOrder = computed(() => items.value.length > 0 && !submitting.value && !pending.value)

// Amounts are USD from the API; formatter converts to JPY for the ja locale.
const money = (amount, decimals = 0) =>
  formatCurrencyWithDecimals(Number(amount) || 0, currentCurrency.value, decimals)

const trendLabel = (trend) => {
  const key = `trends.${trend}`
  const label = t(key)
  return label === key ? trend : label
}

// Validate before formatting; fall back to a dash for bad dates.
const formatDate = (value) => {
  const d = new Date(value)
  if (isNaN(d.getTime())) return '-'
  return d.toLocaleDateString(currentLocale.value === 'ja' ? 'ja-JP' : 'en-US', {
    year: 'numeric', month: 'short', day: 'numeric'
  })
}

// Out-of-order guard: each request gets an increasing id and only the latest
// one is allowed to write state, so a slow earlier response can't overwrite a newer one.
let requestSeq = 0
const fetchRecommendations = async (value) => {
  const seq = ++requestSeq
  try {
    const data = await api.getRestockRecommendations(value)
    if (seq !== requestSeq) return
    recommendation.value = data
    fullRestockCost.value = data.full_restock_cost
    loadError.value = null
  } catch (err) {
    if (seq !== requestSeq) return
    loadError.value = t('restocking.loadFailed')
    console.error('Restock recommendations error:', err)
  } finally {
    if (seq === requestSeq) pending.value = false
  }
}

// Debounce slider drags: wait until the value is stable for DEBOUNCE_MS.
let debounceTimer = null
watch(budget, (value) => {
  if (initialLoading.value) return
  placedOrder.value = null
  orderError.value = null
  pending.value = true
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => fetchRecommendations(value), DEBOUNCE_MS)
})

const placeOrder = async () => {
  if (!canPlaceOrder.value) return
  submitting.value = true
  orderError.value = null
  placedOrder.value = null
  try {
    // Only SKU + quantity are sent; the server computes prices itself.
    placedOrder.value = await api.createRestockOrder({
      items: items.value.map(i => ({ item_sku: i.item_sku, quantity: i.recommended_quantity })),
      budget: budget.value
    })
  } catch (err) {
    const detail = err.response?.data?.detail
    // 422 returns a list of validation objects; 400 returns a string.
    const message = typeof detail === 'string'
      ? detail
      : Array.isArray(detail) ? detail.map(d => d.msg).join('; ') : null
    orderError.value = `${t('restocking.orderFailed')}${message ? ': ' + message : ''}`
    console.error('Place restock order error:', err)
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    // full_restock_cost is returned regardless of budget; use it to size the slider, then default to ~50%.
    const probe = await api.getRestockRecommendations(0)
    fullRestockCost.value = probe.full_restock_cost
    const half = Math.round(sliderMax.value / 2 / SLIDER_STEP) * SLIDER_STEP
    // Set budget before clearing initialLoading so the watcher doesn't fire a duplicate fetch.
    budget.value = half
    const seq = ++requestSeq
    const data = half === 0 ? probe : await api.getRestockRecommendations(half)
    if (seq === requestSeq) {
      recommendation.value = data
    }
  } catch (err) {
    loadError.value = t('restocking.loadFailed')
    console.error('Restock init error:', err)
  } finally {
    initialLoading.value = false
  }
})

onBeforeUnmount(() => {
  clearTimeout(debounceTimer)
  requestSeq++ // invalidate any in-flight response
})
</script>

<style scoped>
.budget-value {
  font-size: var(--text-xl);
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  font-variant-numeric: tabular-nums;
}

.budget-slider {
  width: 100%;
  accent-color: var(--color-accent);
  cursor: pointer;
}

.budget-slider:disabled { cursor: not-allowed; }

.slider-scale {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: var(--space-1);
}

.num { text-align: right; }

/* Dim table while a debounced fetch is pending */
.table-container.stale {
  opacity: 0.6;
  transition: opacity var(--transition-fast);
}

table { min-width: 720px; }

/* Alerts: token-based, inside the card flow */
.success-message {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-4);
  background: var(--color-success-soft);
  border: 1px solid var(--color-success);
  color: var(--color-success);
  padding: var(--space-4);
  border-radius: var(--radius-md);
  margin: 0 0 var(--space-4);
}

.view-orders-link {
  color: var(--color-accent);
  font-weight: var(--weight-semibold);
  text-decoration: none;
  white-space: nowrap;
}

.view-orders-link:hover { text-decoration: underline; }

.empty-title {
  font-weight: var(--weight-semibold);
  color: var(--color-text);
  margin-bottom: var(--space-1);
}
</style>
