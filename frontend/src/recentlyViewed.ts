// Product pages the shopper opened, newest first, remembered in this browser only.
const KEY = 'campus-customs:recently-viewed'
const MAX_ITEMS = 8

export function getRecentlyViewed(): string[] {
  try {
    const saved = JSON.parse(localStorage.getItem(KEY) ?? '[]')
    return Array.isArray(saved) ? saved.filter((id): id is string => typeof id === 'string') : []
  } catch {
    return [] // private windows or blocked storage: just show nothing
  }
}

export function rememberViewed(productId: string) {
  try {
    const ids = [productId, ...getRecentlyViewed().filter((id) => id !== productId)].slice(0, MAX_ITEMS)
    localStorage.setItem(KEY, JSON.stringify(ids))
  } catch {
    // storage unavailable; nothing to remember
  }
}
