import { useState, type InputHTMLAttributes } from 'react'

type FieldProps = InputHTMLAttributes<HTMLInputElement> & {
  id: string
  label: string
  error?: string
  hint?: string
  // Adds a Show/Hide button to a password field.
  revealable?: boolean
}

export default function Field({ id, label, error, hint: hintText, revealable, type, ...inputProps }: FieldProps) {
  const [shown, setShown] = useState(false)
  // The error replaces the hint, so the field never shows two similar messages.
  const hint = error ? undefined : hintText
  const describedBy = [hint && `${id}-hint`, error && `${id}-error`].filter(Boolean).join(' ') || undefined

  return (
    <div className={`field${error ? ' field--error' : ''}`}>
      <label htmlFor={id}>{label}</label>
      <div className="field__control">
        <input
          id={id}
          name={id}
          type={revealable && shown ? 'text' : type}
          aria-invalid={error ? true : undefined}
          aria-describedby={describedBy}
          {...inputProps}
        />
        {revealable && (
          <button
            type="button"
            className="field__reveal"
            aria-controls={id}
            aria-pressed={shown}
            onClick={() => setShown((isShown) => !isShown)}
          >
            {shown ? 'Hide' : 'Show'}
            <span className="visually-hidden"> {label.toLowerCase()}</span>
          </button>
        )}
      </div>
      {hint && (
        <p id={`${id}-hint`} className="field__hint">
          {hint}
        </p>
      )}
      {error && (
        <p id={`${id}-error`} className="field__error">
          {error}
        </p>
      )}
    </div>
  )
}
