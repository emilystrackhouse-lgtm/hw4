import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const API_URL = 'http://127.0.0.1:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // 5173–5176 are used by the lecture apps in this workspace.
    port: 5177,
    strictPort: true,
    // The FastAPI backend (../backend/main.py) serves products and images.
    proxy: {
      '/api': API_URL,
      '/media': API_URL,
    },
  },
})
