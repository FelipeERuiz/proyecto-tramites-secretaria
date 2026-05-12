import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      // Todo lo que empiece con /api se redirige al backend Django
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      }
    }
  }
})