// Single source of truth for the sidebar breakpoints (JS side).
// CSS media queries cannot read custom properties, so the same literals are
// repeated in App.vue, AppSidebar.vue and AppTopbar.vue. Change all four together.
//
//   PHONE   < 640px          off-canvas drawer + top-bar menu button
//   COMPACT 640px - 1279px   icons-only rail; expanding shows a temporary overlay
//   WIDE    >= 1280px        expanded by default; manual collapse persisted
//
// 639.98px (not 639px) so fractional viewport widths never fall in a gap.
export const PHONE_QUERY = '(max-width: 639.98px)'
export const WIDE_QUERY = '(min-width: 1280px)'
