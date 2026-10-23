import { useState, type ChangeEvent, type FormEvent } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router'
import { errorMessage, logIn } from '../api.ts'
import { useAuth } from '../auth.ts'
import Field from '../components/Field.tsx'
import { focusFirstError, isEmail, type Errors } from '../forms.ts'
import { usePageTitle } from '../usePageTitle.ts'

type LoginForm = { email: string; password: string }

function validate(form: LoginForm): Errors<LoginForm> {
  const errors: Errors<LoginForm> = {}
  if (!isEmail(form.email)) errors.email = 'Enter the email address you signed up with.'
  if (!form.password) errors.password = 'Enter your password.'
  return errors
}

export default function Login() {
  usePageTitle('Log in')
  const { user, setUser } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  // Send shoppers back to the page that asked them to log in.
  const returnTo = (location.state as { from?: string } | null)?.from ?? '/account'

  const [form, setForm] = useState<LoginForm>({ email: '', password: '' })
  const [errors, setErrors] = useState<Errors<LoginForm>>({})
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (user && !submitting) return <Navigate to={returnTo} replace />

  const update = (key: keyof LoginForm) => (event: ChangeEvent<HTMLInputElement>) => {
    const { value } = event.target
    setForm((current) => ({ ...current, [key]: value }))
    setErrors((current) => ({ ...current, [key]: undefined }))
    setFormError('')
  }

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const found = validate(form)
    setErrors(found)
    if (focusFirstError(found, ['email', 'password'])) return

    setSubmitting(true)
    setFormError('')
    try {
      setUser(await logIn(form.email.trim(), form.password))
      navigate(returnTo, { replace: true })
    } catch (error) {
      setFormError(errorMessage(error))
      setForm((current) => ({ ...current, password: '' }))
      setSubmitting(false)
    }
  }

  return (
    <section className="auth">
      <div className="auth__card">
        <p className="eyebrow">Welcome back</p>
        <h1>Log in</h1>
        <p className="auth__intro">Good to see you again. Sign in to your Campus Customs account.</p>

        {formError && (
          <p className="form-alert" role="alert">
            {formError}
          </p>
        )}

        <form onSubmit={onSubmit} noValidate aria-busy={submitting}>
          <Field
            id="email"
            label="Email"
            type="email"
            autoComplete="email"
            value={form.email}
            onChange={update('email')}
            error={errors.email}
          />
          <Field
            id="password"
            label="Password"
            type="password"
            autoComplete="current-password"
            revealable
            value={form.password}
            onChange={update('password')}
            error={errors.password}
          />
          <button type="submit" className="button button--primary button--block" disabled={submitting}>
            {submitting ? 'Logging in…' : 'Log in'}
          </button>
        </form>

        <p className="auth__switch">
          New to Campus Customs? <Link to="/create-account">Create an account</Link>
        </p>
      </div>
    </section>
  )
}
