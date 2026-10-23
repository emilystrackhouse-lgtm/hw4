import { Link } from 'react-router'
import { usePageTitle } from '../usePageTitle.ts'

export default function NotFound() {
  usePageTitle('Page not found')

  return (
    <section className="auth">
      <div className="auth__card">
        <p className="eyebrow">404</p>
        <h1>This page wandered off campus</h1>
        <p className="auth__intro">We couldn't find what you were looking for. Let's get you back on track.</p>
        <Link to="/" className="button button--primary button--block">
          Back to home
        </Link>
      </div>
    </section>
  )
}
