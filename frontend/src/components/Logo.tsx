import { Link } from 'react-router'
import { FOUNDED } from '../data/shop.ts'

type LogoProps = {
  onClick?: () => void
  tone?: 'dark' | 'light'
}

export default function Logo({ onClick, tone = 'dark' }: LogoProps) {
  return (
    <Link to="/" className={`logo logo--${tone}`} onClick={onClick} aria-label="Campus Customs home">
      <span className="logo__name" aria-hidden="true">
        <span>Campus</span>
        <span>Customs</span>
      </span>
      <span className="logo__est" aria-hidden="true">
        Est. {FOUNDED}
      </span>
    </Link>
  )
}
