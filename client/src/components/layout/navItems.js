// Single source of truth for navigation; consumed by the sidebar and the top bar title.
// `exact` makes "/" active only on the home route instead of on every route.
export const navSections = [
  {
    labelKey: null, // null = no section heading
    items: [{ labelKey: 'nav.overview', path: '/', icon: 'home', exact: true }]
  },
  {
    labelKey: 'nav.sections.operations',
    items: [
      { labelKey: 'nav.inventory', path: '/inventory', icon: 'box' },
      { labelKey: 'nav.orders', path: '/orders', icon: 'clipboard' },
      { labelKey: 'nav.demandForecast', path: '/demand', icon: 'trending' },
      { labelKey: 'nav.restocking', path: '/restocking', icon: 'truck' }
    ]
  },
  {
    labelKey: 'nav.sections.insights',
    items: [
      { labelKey: 'nav.finance', path: '/spending', icon: 'wallet' },
      { labelKey: 'nav.reports', path: '/reports', icon: 'chart' }
    ]
  }
]

export const isNavItemActive = (item, currentPath) =>
  item.exact
    ? currentPath === item.path
    : currentPath === item.path || currentPath.startsWith(item.path + '/')

export const findNavItem = (currentPath) =>
  navSections.flatMap((s) => s.items).find((item) => isNavItemActive(item, currentPath))
