import { FOUNDED } from '../data/shop.ts'

type SealProps = {
  className?: string
}

// Circular "since 1975" badge drawn in SVG so it scales cleanly.
export default function Seal({ className = '' }: SealProps) {
  return (
    <svg
      className={`seal ${className}`}
      viewBox="0 0 200 200"
      role="img"
      aria-label={`Campus Customs, New Haven, Connecticut, established ${FOUNDED}`}
    >
      <defs>
        <path id="seal-ring" d="M 100,100 m -76,0 a 76,76 0 1,1 152,0 a 76,76 0 1,1 -152,0" />
      </defs>
      <circle cx="100" cy="100" r="97" className="seal__outer" />
      <circle cx="100" cy="100" r="60" className="seal__inner" />
      <text className="seal__ring-text">
        <textPath href="#seal-ring" textLength="470" lengthAdjust="spacing">
          Campus Customs • New Haven, Connecticut •
        </textPath>
      </text>
      <text x="100" y="86" textAnchor="middle" className="seal__est">
        Est.
      </text>
      <text x="100" y="124" textAnchor="middle" className="seal__year">
        {FOUNDED}
      </text>
    </svg>
  )
}
