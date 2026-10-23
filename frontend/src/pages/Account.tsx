import { useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router'
import { formatMemberSince, useAuth } from '../auth.ts'
import { usePageTitle } from '../usePageTitle.ts'

export default function Account() {
  usePageTitle('My account')
  const { user, checking, signOut } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [signingOut, setSigningOut] = useState(false)
  const justJoined = (location.state as { welcome?: boolean } | null)?.welcome

  if (checking) {
    return (
      <section className="auth">
        <p role="status">Loading your account…</p>
      </section>
    )
  }
  if (!user) return <Navigate to="/login" replace state={{ from: '/account' }} />

  const onSignOut = async () => {
    setSigningOut(true)
    // Leave first, so this page doesn't redirect to Log in on the way out.
    navigate('/', { replace: true })
    await signOut()
  }

  return (
    <section className="auth">
      <div className="auth__card auth__card--wide">
        <p className="eyebrow">{justJoined ? 'Welcome to the family' : 'My account'}</p>
        <h1>{justJoined ? `You're in, ${user.first_name}!` : `Hi, ${user.first_name}`}</h1>
        <p className="auth__intro">
          {justJoined
            ? 'Your Campus Customs account is ready. You can log in anytime with your email and password.'
            : 'Here are the details on your Campus Customs account.'}
        </p>

        <dl className="account-details">
          <div>
            <dt>Name</dt>
            <dd>
              {user.first_name} {user.last_name}
            </dd>
          </div>
          <div>
            <dt>Email</dt>
            <dd>{user.email}</dd>
          </div>
          <div>
            <dt>Member since</dt>
            <dd>{formatMemberSince(user.member_since)}</dd>
          </div>
        </dl>

        <div className="account-actions">
          <Link to="/products" className="button button--primary">
            Shop products
          </Link>
          <button type="button" className="button button--outline" onClick={onSignOut} disabled={signingOut}>
            {signingOut ? 'Logging out…' : 'Log out'}
          </button>
        </div>
      </div>
    </section>
  )
}
