export function formatPrice(price: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: Number.isInteger(price) ? 0 : 2,
  }).format(price)
}

export function capitalize(text: string) {
  return text.charAt(0).toUpperCase() + text.slice(1)
}

// Swatch colors for the catalogue's 14 standard color labels.
const SWATCHES: Record<string, string> = {
  navy: '#14284b',
  blue: '#2f6db3',
  'light blue': '#9cc3e6',
  white: '#ffffff',
  cream: '#f1e7d0',
  'heather gray': '#b9bcc0',
  gray: '#8a8f96',
  'charcoal gray': '#4a4f57',
  black: '#111111',
  red: '#c8102e',
  'dusty coral': '#d98c7a',
  yellow: '#f2c230',
  gold: '#c9a227',
  green: '#2e7d4f',
}

export function swatchColor(color: string) {
  return SWATCHES[color] ?? '#cccccc'
}
