import { useEffect } from 'react'
import { Outlet, useLocation } from 'react-router'
import { FOUNDED } from '../data/shop.ts'
import ChatProvider from './ChatProvider.tsx'
import ChatWidget from './ChatWidget.tsx'
import Footer from './Footer.tsx'
import NavBar from './NavBar.tsx'
import Spores from './Spores.tsx'

export default function Layout() {
  const { pathname, hash } = useLocation()

  // Start each new page at the top, unless the link points to a section.
  useEffect(() => {
    if (hash) {
      document.getElementById(hash.slice(1))?.scrollIntoView()
    } else {
      window.scrollTo(0, 0)
    }
  }, [pathname, hash])

  return (
    <ChatProvider>
      <Spores />
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <div className="announcement">
        <p className="container">
          Family-run and right across from Yale since {FOUNDED}
          <span className="announcement__divider" aria-hidden="true">
            •
          </span>
          <span className="announcement__extra">Every style in sizes XS–XXL</span>
        </p>
      </div>
      <NavBar />
      <main id="main" tabIndex={-1}>
        <Outlet />
      </main>
      <Footer />
      <ChatWidget />
    </ChatProvider>
  )
}
