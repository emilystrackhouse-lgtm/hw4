import { useEffect, useState } from 'react'
import { NavLink, useNavigate } from 'react-router'
import { useAuth } from '../auth.ts'
import Logo from './Logo.tsx'

const MAIN_LINKS = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Products', end: false },
  { to: '/about', label: 'About Us', end: false },
]

export default function NavBar() {
  const [open, setOpen] = useState(false)
  const close = () => setOpen(false)
  const { user, checking, signOut } = useAuth()
  const navigate = useNavigate()

  const onSignOut = async () => {
    close()
    // Leave first, so a members-only page doesn't redirect to Log in on the way out.
    navigate('/')
    await signOut()
  }

  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open])

  return (
    <header className="site-header">
      <div className="container site-header__inner">
        <Logo onClick={close} />

        <button
          type="button"
          className="nav-toggle"
          aria-expanded={open}
          aria-controls="site-nav"
          onClick={() => setOpen((isOpen) => !isOpen)}
        >
          <span className={`nav-toggle__icon${open ? ' is-open' : ''}`} aria-hidden="true">
            <span />
            <span />
            <span />
          </span>
          {open ? 'Close' : 'Menu'}
        </button>

        <nav id="site-nav" className={`site-nav${open ? ' is-open' : ''}`} aria-label="Main">
          <ul className="site-nav__links">
            {MAIN_LINKS.map((link) => (
              <li key={link.to}>
                <NavLink to={link.to} end={link.end} className="site-nav__link" onClick={close}>
                  {link.label}
                </NavLink>
              </li>
            ))}
          </ul>
          <div className="site-nav__account">
            {user ? (
              <>
                <NavLink to="/account" className="site-nav__link" onClick={close}>
                  Hi, {user.first_name}
                </NavLink>
                <button type="button" className="button button--outline button--small" onClick={onSignOut}>
                  Log out
                </button>
              </>
            ) : (
              // Hidden until the login check finishes, so logged-in shoppers don't see a flash of these links.
              <div className={`site-nav__guest${checking ? ' is-checking' : ''}`}>
                <NavLink to="/login" className="site-nav__link" onClick={close}>
                  Log in
                </NavLink>
                <NavLink to="/create-account" className="button button--primary button--small" onClick={close}>
                  Create account
                </NavLink>
              </div>
            )}
          </div>
        </nav>
      </div>
    </header>
  )
}
