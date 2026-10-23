import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router'
import {
  ApiError,
  fetchProduct,
  fetchProducts,
  useApi,
  type InventoryItem,
  type Product as ProductSummary,
  type ProductDetail as Product,
} from '../api.ts'
import { useChat } from '../chat.ts'
import ColorList from '../components/ColorList.tsx'
import ProductStrip from '../components/ProductStrip.tsx'
import { styleFor } from '../data/shop.ts'
import { capitalize, formatPrice } from '../format.ts'
import { getRecentlyViewed, rememberViewed } from '../recentlyViewed.ts'
import { usePageTitle } from '../usePageTitle.ts'

const LOW_STOCK = 5
const SIMILAR_COUNT = 4

// Words in a product ID that say what it's for (a college, sport, school, or family member).
const GENERIC_WORDS = new Set(['yale', 'sports', 't', 'shirt', 'hoodie', 'crewneck', 'zip', '1', '4', 'left', 'chest', 'logo', 'college', 'school', 'of'])
const themeWords = (productId: string) => productId.split('-').filter((word) => !GENERIC_WORDS.has(word))

// Same style group, in stock, sharing a theme (Saybrook, Dad, hockey…) first, then closest in price.
function similarProducts(product: Product, all: ProductSummary[]) {
  const style = styleFor(product.garment_type)
  const theme = new Set(themeWords(product.product_id))
  return all
    .filter((p) => p.product_id !== product.product_id && p.total_stock > 0)
    .map((p) => {
      const sameStyle = style ? style.garmentTypes.includes(p.garment_type) : p.garment_type === product.garment_type
      const sharedTheme = themeWords(p.product_id).filter((word) => theme.has(word)).length
      return { p, score: sharedTheme * 3 + (sameStyle ? 2 : 0), priceGap: Math.abs(p.price - product.price) }
    })
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score || a.priceGap - b.priceGap || a.p.name.localeCompare(b.p.name))
    .slice(0, SIMILAR_COUNT)
    .map((item) => item.p)
}

function stockLabel(quantity: number) {
  if (quantity === 0) return 'Sold out'
  if (quantity <= LOW_STOCK) return `Only ${quantity} left`
  return 'In stock'
}

function stockSummary(inventory: InventoryItem[]) {
  const available = inventory.filter((item) => item.quantity > 0).map((item) => item.size)
  const soldOut = inventory.filter((item) => item.quantity === 0).map((item) => item.size)
  if (available.length === 0) return 'Sold out in every size right now.'
  const inStock = `In stock in ${available.join(', ')}.`
  return soldOut.length ? `${inStock} Sold out in ${soldOut.join(', ')}.` : `${inStock} Every size is available.`
}

export default function ProductDetail() {
  const { productId = '' } = useParams()
  const { state, retry } = useApi((signal) => fetchProduct(productId, signal), productId)
  usePageTitle(state.status === 'ready' ? state.data.name : state.status === 'error' ? 'Product unavailable' : 'Product')

  if (state.status === 'loading') {
    return (
      <div className="container product product--loading">
        <p className="visually-hidden" role="status">
          Loading product…
        </p>
        <div className="product__layout" aria-hidden="true">
          <div className="product__media skeleton-block" />
          <div className="product__info">
            <span className="skeleton-line skeleton-line--short" />
            <span className="skeleton-line skeleton-line--title" />
            <span className="skeleton-line" />
            <span className="skeleton-line skeleton-line--wide" />
          </div>
        </div>
      </div>
    )
  }

  if (state.status === 'error') {
    const notFound = state.error instanceof ApiError && state.error.status === 404
    return (
      <section className="auth">
        <div className="auth__card" role="alert">
          <p className="eyebrow">{notFound ? 'Not found' : 'Something went wrong'}</p>
          <h1>{notFound ? "We can't find that item" : "We couldn't load this item"}</h1>
          <p className="auth__intro">
            {notFound
              ? 'It may have sold through or moved. Take a look at the rest of the collection.'
              : "Make sure the shop's server is running, then try again."}
          </p>
          {notFound ? (
            <Link to="/products" className="button button--primary button--block">
              Browse products
            </Link>
          ) : (
            <button type="button" className="button button--primary button--block" onClick={retry}>
              Try again
            </button>
          )}
        </div>
      </section>
    )
  }

  return <ProductView product={state.data} />
}

function ProductView({ product }: { product: Product }) {
  const { openWith } = useChat()
  const style = styleFor(product.garment_type)
  const { state: catalogue } = useApi(fetchProducts, 'products')
  // Captured before this visit is remembered, so the current product isn't in its own "recently viewed" row.
  const [recentIds] = useState(() => getRecentlyViewed().filter((id) => id !== product.product_id))

  useEffect(() => {
    rememberViewed(product.product_id)
  }, [product.product_id])

  const all = catalogue.status === 'ready' ? catalogue.data : []
  const byId = new Map(all.map((p) => [p.product_id, p]))
  const similar = similarProducts(product, all)
  const recent = recentIds
    .map((id) => byId.get(id))
    .filter((p): p is ProductSummary => Boolean(p) && !similar.some((s) => s.product_id === p!.product_id))
    .slice(0, SIMILAR_COUNT)

  return (
    <div className="container product">
      <nav aria-label="Breadcrumb" className="breadcrumb">
        <ol>
          <li>
            <Link to="/products">Products</Link>
          </li>
          {style && (
            <li>
              <Link to={`/products?style=${style.slug}`}>{style.name}</Link>
            </li>
          )}
          <li aria-current="page">{product.name}</li>
        </ol>
      </nav>

      <div className="product__layout">
        <div className="product__media">
          <img src={product.image_url} alt={product.name} width={600} height={600} />
        </div>

        <div className="product__info">
          <p className="eyebrow">{capitalize(product.garment_type)}</p>
          <h1 className="product__title">{product.name}</h1>
          <p className="product__price">{formatPrice(product.price)}</p>
          <p className="product__description">{product.description}</p>

          <section className="product__section" aria-labelledby="sizes-heading">
            <h2 id="sizes-heading" className="product__label">
              Sizes &amp; stock
            </h2>
            <p className="product__stock-summary">{stockSummary(product.inventory)}</p>
            <ul className="size-grid">
              {product.inventory.map((item) => (
                <li
                  key={item.size}
                  className={`size${item.quantity === 0 ? ' size--out' : item.quantity <= LOW_STOCK ? ' size--low' : ''}`}
                >
                  <span className="size__name">{item.size}</span>
                  <span className="size__status">{stockLabel(item.quantity)}</span>
                </li>
              ))}
            </ul>
          </section>

          <section className="product__section" aria-labelledby="colors-heading">
            <h2 id="colors-heading" className="product__label">
              Colors in this design
            </h2>
            <ColorList colors={product.colors} variant="full" />
          </section>

          <div className="product__actions">
            <button
              type="button"
              className="button button--primary"
              onClick={() => openWith(`Hi! I have a question about the ${product.name}.`)}
            >
              Ask about this item
            </button>
            <Link to={style ? `/products?style=${style.slug}` : '/products'} className="button button--outline">
              More {style ? style.name.toLowerCase() : 'products'}
            </Link>
          </div>

          {product.search_tags.length > 0 && (
            <section className="product__section" aria-labelledby="tags-heading">
              <h2 id="tags-heading" className="product__label">
                Tags
              </h2>
              <ul className="tag-list">
                {product.search_tags.map((tag) => (
                  <li key={tag}>{tag}</li>
                ))}
              </ul>
            </section>
          )}
        </div>
      </div>

      <ProductStrip id="similar" title="You might also like" products={similar} />
      <ProductStrip id="recently-viewed" title="Recently viewed" products={recent} />
    </div>
  )
}
