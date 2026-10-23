import { useState, type ReactNode } from 'react'
import type { SearchResults } from '../api.ts'
import { ChatContext } from '../chat.ts'

export default function ChatProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)
  const [draft, setDraft] = useState('')
  const [searchResults, setSearchResults] = useState<SearchResults | null>(null)

  const openWith = (text: string) => {
    setDraft(text)
    setOpen(true)
  }

  return <ChatContext.Provider value={{ open, setOpen, draft, setDraft, openWith, searchResults, setSearchResults }}>{children}</ChatContext.Provider>
}
