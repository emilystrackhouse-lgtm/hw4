import { useEffect, useState } from 'react'

// Shapes returned by the FastAPI backend (../backend/main.py).
export type InventoryItem = { size: string; quantity: number }

export type Product = {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  price: number
  image_url: string
  total_stock: number
  sizes_in_stock: string[]
}

export type ProductDetail = Product & {
  search_tags: string[]
  inventory: InventoryItem[]
}

export type User = {
  id: number
  first_name: string
  last_name: string
  email: string
  member_since: string
}

export type SignupForm = {
  first_name: string
  last_name: string
  email: string
  password: string
  confirm_password: string
}

export class ApiError extends Error {
  status: number
  // The form field the server's message is about, when there is one.
  field?: string

  constructor(status: number, message?: string, field?: string) {
    super(message ?? `Request failed with status ${status}`)
    this.status = status
    this.field = field
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init)
  if (!response.ok) {
    // The backend sends {detail: {message, field}} for errors a shopper can fix.
    const body = await response.json().catch(() => null)
    const detail = body?.detail
    if (detail && typeof detail === 'object') throw new ApiError(response.status, detail.message, detail.field ?? undefined)
    throw new ApiError(response.status, typeof detail === 'string' ? detail : undefined)
  }
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

const postJson = <T>(path: string, body?: unknown) =>
  request<T>(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })

export const fetchProducts = (signal?: AbortSignal) => request<Product[]>('/api/products', { signal })

export const fetchProduct = (productId: string, signal?: AbortSignal) =>
  request<ProductDetail>(`/api/products/${encodeURIComponent(productId)}`, { signal })

// The session lives in an HttpOnly cookie the browser sends automatically;
// page scripts never see the token.
export const fetchCurrentUser = () => request<User | null>('/api/auth/me')
export const logIn = (email: string, password: string) => postJson<User>('/api/auth/login', { email, password })
export const signUp = (form: SignupForm) => postJson<User>('/api/auth/signup', form)
export const logOut = () => postJson<void>('/api/auth/logout')

// --- Shop assistant chat (POST /api/chat) ---

export type ChatTurn = { role: 'user' | 'assistant'; content: string }

export type ProductCard = {
  product_id: string
  name: string
  price: number
  image_url: string
  url: string
  color: string
  sizes_in_stock: string[]
}

// Products from the assistant's catalog search, shown on the Products page.
export type SearchResults = { title: string; products: Product[] }

export type ChatReply = { reply: string; products: ProductCard[]; search: SearchResults | null }

// The page the shopper is on, so "this" can mean the product they're looking at.
export type PageContext = { path: string; product_id: string | null }

// Guests' messages carry the recent conversation. For logged-in customers the
// backend uses their saved history instead (and ignores this).
export const MAX_CHAT_HISTORY = 20

export const sendChatMessage = (message: string, history: ChatTurn[], page: PageContext) =>
  postJson<ChatReply>('/api/chat', { message, history: history.slice(-MAX_CHAT_HISTORY), page })

export type SavedChatMessage = { role: 'user' | 'assistant'; content: string; products: ProductCard[]; created_at: string }

// A logged-in customer's saved conversation ([] for guests).
export const fetchChatHistory = () => request<SavedChatMessage[]>('/api/chat/history')

// A shopper-friendly message for any failed request.
export function errorMessage(error: unknown) {
  if (error instanceof ApiError && error.status < 500 && error.message) return error.message
  if (error instanceof TypeError) return "We couldn't reach the shop's server. Check your connection and try again."
  return 'Something went wrong on our end. Please try again.'
}

type ApiState<T> = { status: 'loading' } | { status: 'error'; error: unknown } | { status: 'ready'; data: T }

// Loads data when `key` changes, with loading and error states and a retry.
export function useApi<T>(load: (signal: AbortSignal) => Promise<T>, key: string) {
  const [attempt, setAttempt] = useState(0)
  const requestKey = `${key}#${attempt}`
  const [result, setResult] = useState<{ requestKey: string; state: ApiState<T> } | null>(null)

  useEffect(() => {
    const controller = new AbortController()
    load(controller.signal).then(
      (data) => setResult({ requestKey, state: { status: 'ready', data } }),
      (error: unknown) => {
        if (!controller.signal.aborted) setResult({ requestKey, state: { status: 'error', error } })
      },
    )
    return () => controller.abort()
    // `load` is recreated on every render; `requestKey` is what identifies the request.
  }, [requestKey]) // eslint-disable-line react-hooks/exhaustive-deps

  // Until the current request finishes, report loading (even if an older result is stored).
  const state: ApiState<T> = result?.requestKey === requestKey ? result.state : { status: 'loading' }
  return { state, retry: () => setAttempt((count) => count + 1) }
}
