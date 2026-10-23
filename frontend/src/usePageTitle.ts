import { useEffect } from 'react'

const SITE_TITLE = 'Campus Customs | Yale Apparel Across from Campus'

export function usePageTitle(title?: string) {
  useEffect(() => {
    document.title = title ? `${title} | Campus Customs` : SITE_TITLE
  }, [title])
}
