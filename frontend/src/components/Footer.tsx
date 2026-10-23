import { Link } from 'react-router'
import { useAuth } from '../auth.ts'
import { FOUNDED } from '../data/shop.ts'
import Logo from './Logo.tsx'

const CURRENT_YEAR = new Date().getFullYear()

export default function Footer() {
  const { user } = useAuth()

  return (
    <footer className="site-footer">
      <div className="container site-footer__grid">
        <div className="site-footer__brand">
          <Logo tone="light" />
          <p>
            Yale apparel from the family shop across the street from campus. Printed, stitched, and folded with
            care in New Haven since {FOUNDED}.
          </p>
        </div>
        <nav className="site-footer__col" aria-label="Shop">
          <h2>Shop</h2>
          <ul>
            <li>
              <Link to="/products">All products</Link>
            </li>
            <li>
              <Link to="/products?style=hoodies">Hoodies</Link>
            </li>
            <li>
              <Link to="/products?style=crewnecks">Crewnecks</Link>
            </li>
            <li>
              <Link to="/products?style=t-shirts">T-shirts</Link>
            </li>
          </ul>
        </nav>
        <nav className="site-footer__col" aria-label="Company">
          <h2>Company</h2>
          <ul>
            <li>
              <Link to="/about">About us</Link>
            </li>
            <li>
              <Link to="/about#services">Custom printing &amp; embroidery</Link>
            </li>
          </ul>
        </nav>
        <nav className="site-footer__col" aria-label="Account">
          <h2>Account</h2>
          <ul>
            {user ? (
              <li>
                <Link to="/account">My account</Link>
              </li>
            ) : (
              <>
                <li>
                  <Link to="/login">Log in</Link>
                </li>
                <li>
                  <Link to="/create-account">Create account</Link>
                </li>
              </>
            )}
          </ul>
        </nav>
      </div>
      <div className="container site-footer__bottom">
        <p>© {CURRENT_YEAR} Campus Customs · New Haven, Connecticut</p>
        <p>Go Bulldogs.</p>
      </div>
    </footer>
  )
}
