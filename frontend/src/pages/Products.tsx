import { useState } from 'react'
import { Link, useSearchParams } from 'react-router'
import { fetchProducts, useApi, type Product } from '../api.ts'
import { useChat } from '../chat.ts'
import ProductCard, { ProductCardSkeleton } from '../components/ProductCard.tsx'
import ProductStrip from '../components/ProductStrip.tsx'
import { STYLES } from '../data/shop.ts'
import { getRecentlyViewed } from '../recentlyViewed.ts'
import { usePageTitle } from '../usePageTitle.ts'

const SKELETON_COUNT = 8
const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
const SORTS = {
  featured: { label: 'Featured', compare: () => 0 },
  'price-asc': { label: 'Price: low to high', compare: (a: Product, b: Product) => a.price - b.price },
  'price-desc': { label: 'Price: high to low', compare: (a: Product, b: Product) => b.price - a.price },
  name: { label: 'Name: A to Z', compare: (a: Product, b: Product) => a.name.localeCompare(b.name) },
} as const
type SortKey = keyof typeof SORTS

// Search, size, and sort apply to whatever list is showing (all products, a style, or chat results).
function refine(list: Product[], text: string, size: string, sort: SortKey) {
  const words = text.toLowerCase().split(/\s+/).filter(Boolean)
  const matches = list.filter((p) => {
    const haystack = `${p.name} ${p.description} ${p.colors.join(' ')} ${p.garment_type}`.toLowerCase()
    return words.every((word) => haystack.includes(word)) && (!size || p.sizes_in_stock.includes(size))
  })
  return sort === 'featured' ? matches : [...matches].sort(SORTS[sort].compare)
}

export default function Products() {
  usePageTitle('Products')
  const { state, retry } = useApi(fetchProducts, 'products')
  const [params, setParams] = useSearchParams()
  const activeStyle = STYLES.find((style) => style.slug === params.get('style'))
  const text = params.get('q') ?? ''
  const size = SIZES.includes(params.get('size') ?? '') ? params.get('size')! : ''
  const sort: SortKey = (params.get('sort') ?? '') in SORTS ? (params.get('sort') as SortKey) : 'featured'
  // Read once per visit to the page, so the row doesn't jump around while browsing.
  const [recentIds] = useState(getRecentlyViewed)
  // Results from a chat search ("What hoodies do you have?") replace the grid until cleared.
  const { searchResults, setSearchResults } = useChat()

  // Keeps the other filters in the URL, so a filtered page can be shared or bookmarked.
  const setParam = (key: string, value: string) =>
    setParams(
      (current) => {
        const next = new URLSearchParams(current)
        if (value) next.set(key, value)
        else next.delete(key)
        return next
      },
      { replace: key === 'q' },
    )
  const showStyle = (slug?: string) => {
    setSearchResults(null)
    setParam('style', slug ?? '')
  }
  const clearRefinements = () => setParams(activeStyle ? { style: activeStyle.slug } : {})

  const products = state.status === 'ready' ? state.data : []
  const byStyle = activeStyle ? products.filter((p) => activeStyle.garmentTypes.includes(p.garment_type)) : products
  const base = searchResults ? searchResults.products : byStyle
  const shown = refine(base, text, size, sort)
  const refined = Boolean(text || size)
  const countFor = (garmentTypes: string[]) => products.filter((p) => garmentTypes.includes(p.garment_type)).length
  const byId = new Map(products.map((p) => [p.product_id, p]))
  const recent = recentIds.map((id) => byId.get(id)).filter((p): p is Product => Boolean(p))

  return (
    <>
      <section className="page-hero">
        <div className="container">
          <p className="eyebrow eyebrow--light">The collection</p>
          <h1>Products</h1>
          <p className="page-hero__lede">
            Every piece in the shop comes in sizes XS through XXL. Pick a style, then tap any item for photos, sizes,
            and stock.
          </p>
        </div>
      </section>

      <section className="section section--compact" aria-labelledby="products-heading">
        <div className="container">
          <h2 id="products-heading" className="visually-hidden">
            {searchResults ? searchResults.title : activeStyle ? activeStyle.name : 'All products'}
          </h2>

          <div className="filter-bar" role="group" aria-label="Filter by style">
            <button
              type="button"
              className="chip"
              aria-pressed={!searchResults && !activeStyle}
              onClick={() => showStyle()}
            >
              All{state.status === 'ready' && <span className="chip__count">{products.length}</span>}
            </button>
            {STYLES.map((style) => (
              <button
                key={style.slug}
                type="button"
                className="chip"
                aria-pressed={!searchResults && activeStyle?.slug === style.slug}
                onClick={() => showStyle(style.slug)}
              >
                {style.name}
                {state.status === 'ready' && <span className="chip__count">{countFor(style.garmentTypes)}</span>}
              </button>
            ))}
          </div>

          <div className="toolbar" role="search" aria-label="Find a product">
            <div className="toolbar__field toolbar__field--search">
              <label htmlFor="product-search">Search</label>
              <input
                id="product-search"
                type="search"
                value={text}
                onChange={(event) => setParam('q', event.target.value)}
                placeholder="Try “Saybrook”, “gray”, or “bulldog”"
                autoComplete="off"
              />
            </div>
            <div className="toolbar__field">
              <label htmlFor="product-size">In my size</label>
              <select id="product-size" value={size} onChange={(event) => setParam('size', event.target.value)}>
                <option value="">Any size</option>
                {SIZES.map((s) => (
                  <option key={s} value={s}>
                    {s} in stock
                  </option>
                ))}
              </select>
            </div>
            <div className="toolbar__field">
              <label htmlFor="product-sort">Sort by</label>
              <select id="product-sort" value={sort} onChange={(event) => setParam('sort', event.target.value)}>
                {Object.entries(SORTS).map(([key, option]) => (
                  <option key={key} value={key}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {searchResults && (
            <div className="search-banner" role="status">
              <p>
                <span className="search-banner__label">From the shop assistant</span>
                <strong>{searchResults.title}</strong> · {searchResults.products.length}{' '}
                {searchResults.products.length === 1 ? 'style' : 'styles'}
              </p>
              <button type="button" className="button button--outline button--small" onClick={() => showStyle()}>
                Show all products
              </button>
            </div>
          )}

          {!searchResults && state.status === 'loading' && (
            <>
              <p className="visually-hidden" role="status">
                Loading products…
              </p>
              <ul className="product-grid">
                {Array.from({ length: SKELETON_COUNT }, (_, index) => (
                  <li key={index}>
                    <ProductCardSkeleton />
                  </li>
                ))}
              </ul>
            </>
          )}

          {!searchResults && state.status === 'error' && (
            <div className="notice notice--error" role="alert">
              <h3>We couldn't load the products</h3>
              <p>Make sure the shop's server is running, then try again.</p>
              <button type="button" className="button button--primary" onClick={retry}>
                Try again
              </button>
            </div>
          )}

          {(searchResults || state.status === 'ready') && (
            <>
              <p className="result-count" role="status">
                Showing {shown.length} {shown.length === 1 ? 'style' : 'styles'}
                {!searchResults && activeStyle && ` in ${activeStyle.name}`}
                {text && ` matching “${text}”`}
                {size && ` with ${size} in stock`}
              </p>
              {shown.length > 0 ? (
                <ul className="product-grid">
                  {shown.map((product) => (
                    <li key={product.product_id}>
                      <ProductCard product={product} />
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="notice">
                  <h3>Nothing matches yet</h3>
                  <p>Try a different word or size, or ask the shop assistant for ideas.</p>
                  {refined && (
                    <button type="button" className="button button--primary" onClick={clearRefinements}>
                      Clear search and size
                    </button>
                  )}
                </div>
              )}
            </>
          )}

          <ProductStrip id="recently-viewed" title="Recently viewed" products={recent} />
        </div>
      </section>

      <section className="cta-band">
        <div className="container cta-band__inner">
          <div>
            <h2>Need something custom?</h2>
            <p>Our shop next door prints and stitches gear for teams, clubs, reunions, and events.</p>
          </div>
          <Link to="/about#services" className="button button--light">
            See what we make
          </Link>
        </div>
      </section>
    </>
  )
}
