import { useState, type ChangeEvent, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router'
import { ApiError, errorMessage, signUp } from '../api.ts'
import { useAuth } from '../auth.ts'
import Field from '../components/Field.tsx'
import { focusFirstError, isEmail, type Errors } from '../forms.ts'
import { usePageTitle } from '../usePageTitle.ts'

type SignupForm = {
  firstName: string
  lastName: string
  email: string
  password: string
  confirmPassword: string
}

const FIELD_ORDER: (keyof SignupForm)[] = ['firstName', 'lastName', 'email', 'password', 'confirmPassword']
const MIN_PASSWORD_LENGTH = 8

// The server names fields the way the database does.
const SERVER_FIELDS: Record<string, keyof SignupForm> = {
  first_name: 'firstName',
  last_name: 'lastName',
  email: 'email',
  password: 'password',
  confirm_password: 'confirmPassword',
}

function validate(form: SignupForm): Errors<SignupForm> {
  const errors: Errors<SignupForm> = {}
  if (!form.firstName.trim()) errors.firstName = 'Enter your first name.'
  if (!form.lastName.trim()) errors.lastName = 'Enter your last name.'
  if (!isEmail(form.email)) errors.email = 'Enter a valid email address, like you@yale.edu.'
  if (form.password.length < MIN_PASSWORD_LENGTH) {
    errors.password = `Use at least ${MIN_PASSWORD_LENGTH} characters.`
  }
  if (form.confirmPassword !== form.password || !form.confirmPassword) {
    errors.confirmPassword = 'Passwords need to match.'
  }
  return errors
}

export default function CreateAccount() {
  usePageTitle('Create account')
  const { user, setUser } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState<SignupForm>({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [errors, setErrors] = useState<Errors<SignupForm>>({})
  const [formError, setFormError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (user && !submitting) return <Navigate to="/account" replace />

  const update = (key: keyof SignupForm) => (event: ChangeEvent<HTMLInputElement>) => {
    const { value } = event.target
    setForm((current) => ({ ...current, [key]: value }))
    setErrors((current) => ({ ...current, [key]: undefined }))
    setFormError('')
  }

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const found = validate(form)
    setErrors(found)
    if (focusFirstError(found, FIELD_ORDER)) return

    setSubmitting(true)
    setFormError('')
    try {
      const newUser = await signUp({
        first_name: form.firstName.trim(),
        last_name: form.lastName.trim(),
        email: form.email.trim(),
        password: form.password,
        confirm_password: form.confirmPassword,
      })
      setUser(newUser)
      navigate('/account', { replace: true, state: { welcome: true } })
    } catch (error) {
      const field = error instanceof ApiError && error.field ? SERVER_FIELDS[error.field] : undefined
      if (field) {
        const fieldErrors = { [field]: errorMessage(error) }
        setErrors(fieldErrors)
        focusFirstError(fieldErrors, FIELD_ORDER)
      } else {
        setFormError(errorMessage(error))
      }
      setSubmitting(false)
    }
  }

  return (
    <section className="auth">
      <div className="auth__card auth__card--wide">
        <p className="eyebrow">Join the family</p>
        <h1>Create account</h1>
        <p className="auth__intro">It's free and takes about a minute. Then you're part of the Campus Customs crew.</p>

        {formError && (
          <p className="form-alert" role="alert">
            {formError}
          </p>
        )}

        <form onSubmit={onSubmit} noValidate aria-busy={submitting}>
          <div className="field-row">
            <Field
              id="firstName"
              label="First name"
              autoComplete="given-name"
              value={form.firstName}
              onChange={update('firstName')}
              error={errors.firstName}
            />
            <Field
              id="lastName"
              label="Last name"
              autoComplete="family-name"
              value={form.lastName}
              onChange={update('lastName')}
              error={errors.lastName}
            />
          </div>
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
            autoComplete="new-password"
            revealable
            hint={`At least ${MIN_PASSWORD_LENGTH} characters. A short phrase is easy to remember and hard to guess.`}
            value={form.password}
            onChange={update('password')}
            error={errors.password}
          />
          <Field
            id="confirmPassword"
            label="Confirm password"
            type="password"
            autoComplete="new-password"
            revealable
            value={form.confirmPassword}
            onChange={update('confirmPassword')}
            error={errors.confirmPassword}
          />
          <button type="submit" className="button button--primary button--block" disabled={submitting}>
            {submitting ? 'Creating your account…' : 'Create account'}
          </button>
        </form>

        <p className="auth__switch">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </div>
    </section>
  )
}
