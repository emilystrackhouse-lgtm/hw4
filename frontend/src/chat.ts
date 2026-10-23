import { createContext, useContext } from 'react'
import type { SearchResults } from './api.ts'

export type ChatControls = {
  open: boolean
  setOpen: (open: boolean) => void
  draft: string
  setDraft: (draft: string) => void
  // Opens the chat panel with a message ready to send.
  openWith: (draft: string) => void
  // The latest catalog search from chat, shown on the Products page until cleared.
  searchResults: SearchResults | null
  setSearchResults: (results: SearchResults | null) => void
}

export const ChatContext = createContext<ChatControls | null>(null)

export function useChat() {
  const controls = useContext(ChatContext)
  if (!controls) throw new Error('useChat must be used inside ChatProvider')
  return controls
}
