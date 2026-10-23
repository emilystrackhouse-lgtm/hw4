import type { PointerEvent } from 'react'
import { Link } from 'react-router'
import type { Product } from '../api.ts'
import { formatPrice } from '../format.ts'
import ColorList from './ColorList.tsx'

// Tilts the card a few degrees toward the pointer and moves its glow there.
function followPointer(event: PointerEvent<HTMLAnchorElement>) {
  if (event.pointerType !== 'mouse') return
  const card = event.currentTarget
  const box = card.getBoundingClientRect()
  const x = (event.clientX - box.left) / box.width
  const y = (event.clientY - box.top) / box.height
  card.style.setProperty('--glow-x', `${x * 100}%`)
  card.style.setProperty('--glow-y', `${y * 100}%`)
  card.style.setProperty('--tilt-x', `${(0.5 - y) * 6}deg`)
  card.style.setProperty('--tilt-y', `${(x - 0.5) * 8}deg`)
}

function resetPointer(event: PointerEvent<HTMLAnchorElement>) {
  event.currentTarget.style.setProperty('--tilt-x', '0deg')
  event.currentTarget.style.setProperty('--tilt-y', '0deg')
}

export default function ProductCard({ product }: { product: Product }) {
  const lowStock = product.total_stock > 0 && product.sizes_in_stock.length <= 3
  return (
    <Link
      to={`/products/${product.product_id}`}
      className="product-card"
      onPointerMove={followPointer}
      onPointerLeave={resetPointer}
    >
      <div className="product-card__media">
        <img src={product.image_url} alt="" loading="lazy" width={600} height={600} />
        {lowStock && <span className="product-card__badge">Few sizes left</span>}
      </div>
      <div className="product-card__body">
        <div className="product-card__top">
          <h3 className="product-card__name">{product.name}</h3>
          <p className="product-card__price">{formatPrice(product.price)}</p>
        </div>
        <p className="product-card__description">{product.description}</p>
        <ColorList colors={product.colors} />
      </div>
    </Link>
  )
}

export function ProductCardSkeleton() {
  return (
    <div className="product-card product-card--skeleton" aria-hidden="true">
      <div className="product-card__media" />
      <div className="product-card__body">
        <span className="skeleton-line skeleton-line--wide" />
        <span className="skeleton-line" />
        <span className="skeleton-line skeleton-line--short" />
      </div>
    </div>
  )
}
