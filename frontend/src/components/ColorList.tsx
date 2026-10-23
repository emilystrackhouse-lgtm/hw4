import { capitalize, swatchColor } from '../format.ts'

type ColorListProps = {
  colors: string[]
  // Compact shows swatches plus the main color; full lists every color by name.
  variant?: 'compact' | 'full'
}

export default function ColorList({ colors, variant = 'compact' }: ColorListProps) {
  if (colors.length === 0) return null

  if (variant === 'full') {
    return (
      <ul className="color-list">
        {colors.map((color) => (
          <li key={color}>
            <span className="swatch" style={{ background: swatchColor(color) }} aria-hidden="true" />
            {capitalize(color)}
          </li>
        ))}
      </ul>
    )
  }

  const [main, ...accents] = colors
  return (
    <p className="color-summary">
      <span className="swatches" aria-hidden="true">
        {colors.map((color) => (
          <span key={color} className="swatch" style={{ background: swatchColor(color) }} />
        ))}
      </span>
      <span>
        {capitalize(main)}
        {accents.length > 0 && <span className="visually-hidden"> with {accents.join(', ')}</span>}
      </span>
    </p>
  )
}
