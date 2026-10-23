import { Fragment, useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router'
import { ApiError, errorMessage, fetchChatHistory, sendChatMessage, type ChatTurn, type ProductCard } from '../api.ts'
import { useAuth } from '../auth.ts'
import { useChat } from '../chat.ts'
import { formatPrice } from '../format.ts'

type Message = {
  id: number
  role: 'assistant' | 'user'
  text: string
  products?: ProductCard[]
  // A failed reply is shown to the shopper but never sent back to the assistant as history.
  failed?: boolean
  // Loaded from the customer's saved history when they came back.
  restored?: boolean
}

const greeting = (firstName?: string) =>
  `Hi${firstName ? ` ${firstName}` : ''}! I'm the Campus Customs shop assistant. Ask me about styles, sizes, or what's in stock.`

const SUGGESTIONS = ['What hoodies do you have?', 'Gift ideas for a Yale parent', 'Anything with a bulldog on it?']

// "/products/yale-dad-hoodie" -> "yale-dad-hoodie"
function productIdFromPath(pathname: string) {
  const match = /^\/products\/([^/]+)$/.exec(pathname)
  return match ? decodeURIComponent(match[1]) : null
}

function chatErrorMessage(error: unknown) {
  // Busy, offline, and model errors come with a message written for shoppers.
  if (error instanceof ApiError && [429, 502, 503].includes(error.status)) return error.message
  return errorMessage(error)
}

export default function ChatWidget() {
  const { open, setOpen, draft, setDraft, setSearchResults } = useChat()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const { user } = useAuth()
  // The conversation belongs to whoever is signed in (null = guest). When that changes,
  // the old conversation disappears, and a returning customer's saved one is loaded.
  const owner = user?.id ?? null
  const [chat, setChat] = useState<{ owner: number | null; messages: Message[] }>({ owner: null, messages: [] })
  const conversation = chat.owner === owner ? chat.messages : []
  const setConversation = (update: (current: Message[]) => Message[]) =>
    setChat((current) => ({ owner, messages: update(current.owner === owner ? current.messages : []) }))
  const [waiting, setWaiting] = useState(false)
  const messages: Message[] = [{ id: 0, role: 'assistant', text: greeting(user?.first_name) }, ...conversation]
  const nextId = useRef(1)
  const inputRef = useRef<HTMLInputElement>(null)
  const launcherRef = useRef<HTMLButtonElement>(null)
  const logRef = useRef<HTMLOListElement>(null)

  useEffect(() => {
    if (open) inputRef.current?.focus()
  }, [open])

  useEffect(() => {
    if (owner === null) return
    let cancelled = false
    fetchChatHistory()
      .then((saved) => {
        if (cancelled) return
        const restored = saved.map((message) => ({
          id: nextId.current++,
          role: message.role,
          text: message.content,
          products: message.products,
          restored: true,
        }))
        setChat({ owner, messages: restored })
      })
      .catch(() => {}) // if history can't load, the chat still works from here on
    return () => {
      cancelled = true
    }
  }, [owner])

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight })
  }, [chat, waiting])

  const close = () => {
    setOpen(false)
    launcherRef.current?.focus()
  }

  const add = (message: Omit<Message, 'id'>) =>
    setConversation((current) => [...current, { ...message, id: nextId.current++ }])

  const send = async (text: string) => {
    const question = text.trim()
    if (!question || waiting) return
    const history: ChatTurn[] = conversation
      .filter((message) => !message.failed)
      .map((message) => ({ role: message.role, content: message.text }))

    add({ role: 'user', text: question })
    setDraft('')
    setWaiting(true)
    try {
      const page = { path: pathname, product_id: productIdFromPath(pathname) }
      const { reply, products, search } = await sendChatMessage(question, history, page)
      add({ role: 'assistant', text: reply, products })
      if (search && search.products.length > 0) {
        // Show every match as cards on the Products page; the chat stays open beside it.
        setSearchResults(search)
        if (pathname !== '/products') navigate('/products')
      }
    } catch (error) {
      add({ role: 'assistant', text: chatErrorMessage(error), failed: true })
    } finally {
      setWaiting(false)
      inputRef.current?.focus()
    }
  }

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    void send(draft)
  }

  const onKeyDown = (event: KeyboardEvent<HTMLElement>) => {
    if (event.key === 'Escape') close()
  }

  return (
    <div className="chat">
      <section
        id="chat-panel"
        className="chat__panel"
        role="dialog"
        aria-labelledby="chat-title"
        hidden={!open}
        onKeyDown={onKeyDown}
      >
        <header className="chat__header">
          <span className="chat__avatar" aria-hidden="true">
            CC
          </span>
          <div>
            <h2 id="chat-title">Shop assistant</h2>
            <p>Questions about styles, sizes, and stock</p>
          </div>
          <button type="button" className="chat__close" aria-label="Close chat" onClick={close}>
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </header>

        <ol
          ref={logRef}
          className="chat__messages"
          role="log"
          aria-live="polite"
          aria-label="Conversation"
          aria-busy={waiting}
        >
          {messages.map((message, index) => (
            <Fragment key={message.id}>
            {message.restored && !messages[index - 1]?.restored && (
              <li className="chat__divider" aria-label="Your earlier conversation">
                Earlier conversation
              </li>
            )}
            <li
              className={`chat__message chat__message--${message.role}${message.failed ? ' chat__message--failed' : ''}`}
            >
              <span className="visually-hidden">{message.role === 'user' ? 'You: ' : 'Assistant: '}</span>
              <p className="chat__text">{message.text}</p>
              {message.products && message.products.length > 0 && (
                <ul className="chat__cards" aria-label="Suggested products">
                  {message.products.map((product) => (
                    <li key={product.product_id}>
                      <Link to={product.url} className="chat-card">
                        <img src={product.image_url} alt="" width={64} height={64} loading="lazy" />
                        <span className="chat-card__name">{product.name}</span>
                        <span className="chat-card__meta">
                          {formatPrice(product.price)}
                          {product.sizes_in_stock.length > 0
                            ? ` · ${product.sizes_in_stock.join(', ')}`
                            : ' · Sold out'}
                        </span>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </li>
            {message.restored && !messages[index + 1]?.restored && (
              <li className="chat__divider">Welcome back. Pick up where you left off</li>
            )}
            </Fragment>
          ))}
          {waiting && (
            <li className="chat__message chat__message--assistant chat__typing">
              <span className="visually-hidden">The assistant is typing…</span>
              <span className="chat__dot" aria-hidden="true" />
              <span className="chat__dot" aria-hidden="true" />
              <span className="chat__dot" aria-hidden="true" />
            </li>
          )}
        </ol>

        {conversation.length === 0 && (
          <div className="chat__suggestions" aria-label="Suggested questions">
            {SUGGESTIONS.map((suggestion) => (
              <button key={suggestion} type="button" onClick={() => void send(suggestion)}>
                {suggestion}
              </button>
            ))}
          </div>
        )}

        <form className="chat__form" onSubmit={onSubmit}>
          <label htmlFor="chat-input" className="visually-hidden">
            Your message
          </label>
          <input
            id="chat-input"
            ref={inputRef}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Ask about a product…"
            autoComplete="off"
            maxLength={1000}
          />
          <button
            type="submit"
            className="chat__send"
            disabled={!draft.trim() || waiting}
            aria-label="Send message"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M4 12h15M13 6l6 6-6 6" />
            </svg>
          </button>
        </form>
      </section>

      <button
        ref={launcherRef}
        type="button"
        className="chat__launcher"
        aria-expanded={open}
        aria-controls="chat-panel"
        onClick={() => setOpen(!open)}
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          {open ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M4 5h16v11H9l-5 4V5z" />}
        </svg>
        <span>{open ? 'Close chat' : 'Ask us'}</span>
      </button>
    </div>
  )
}
