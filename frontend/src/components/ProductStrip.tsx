import { Link } from 'react-router'
import type { Product } from '../api.ts'
import { formatPrice } from '../format.ts'

type ProductStripProps = {
  title: string
  products: Product[]
  id: string
}

// A compact, scrollable row of products ("You might also like", "Recently viewed").
export default function ProductStrip({ title, products, id }: ProductStripProps) {
  if (products.length === 0) return null
  return (
    <section className="product-strip" aria-labelledby={id}>
      <h2 id={id} className="product-strip__title">
        {title}
      </h2>
      <ul className="product-strip__list">
        {products.map((product) => (
          <li key={product.product_id}>
            <Link to={`/products/${product.product_id}`} className="strip-card">
              <img src={product.image_url} alt="" width={160} height={160} loading="lazy" />
              <span className="strip-card__name">{product.name}</span>
              <span className="strip-card__price">{formatPrice(product.price)}</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
