export type Errors<T> = Partial<Record<keyof T, string>>

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function isEmail(value: string) {
  return EMAIL_PATTERN.test(value.trim())
}

// Moves keyboard focus to the first field with an error. Returns true if there was one.
export function focusFirstError<T>(errors: Errors<T>, order: (keyof T & string)[]) {
  const first = order.find((key) => errors[key])
  if (first) document.getElementById(first)?.focus()
  return Boolean(first)
}
