<template>
  <svg class="nav-icon" width="20" height="20" viewBox="0 0 24 24" fill="none"
       stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"
       aria-hidden="true">
    <path v-for="d in paths" :key="d" :d="d" />
  </svg>
</template>

<script>
import { computed } from 'vue'

// Minimal Lucide-style path set (inline SVG, no icon library). Unknown names render a dot.
const ICONS = {
  home: ['M3 10.5 12 3l9 7.5', 'M5 9.5V21h14V9.5'],
  box: ['M21 8 12 3 3 8l9 5 9-5Z', 'M3 8v8l9 5 9-5V8', 'M12 13v8'],
  clipboard: ['M9 4h6v3H9z', 'M9 5H6v16h12V5h-3', 'M9 12h6', 'M9 16h4'],
  chart: ['M4 20V10', 'M10 20V4', 'M16 20v-7', 'M22 20H2'],
  trending: ['M3 17l6-6 4 4 8-8', 'M15 7h6v6'],
  wallet: ['M3 7h16a2 2 0 0 1 2 2v10H3z', 'M3 7V5h14v2', 'M16 13h2'],
  truck: ['M3 6h11v10H3z', 'M14 10h4l3 3v3h-7', 'M7 19a2 2 0 1 0 0-.01', 'M17 19a2 2 0 1 0 0-.01'],
  menu: ['M4 6h16', 'M4 12h16', 'M4 18h16'],
  chevronLeft: ['M15 18l-6-6 6-6'],
  chevronRight: ['M9 18l6-6-6-6'],
  close: ['M6 6l12 12', 'M18 6 6 18']
}

export default {
  name: 'NavIcon',
  props: { name: { type: String, required: true } },
  setup(props) {
    const paths = computed(() => ICONS[props.name] || ['M12 12h.01'])
    return { paths }
  }
}
</script>

<style scoped>
.nav-icon { flex-shrink: 0; display: block; }
</style>
