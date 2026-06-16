import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: '0.0.0.0', // Чтобы Vite был доступен за пределами контейнера
    port: 5173,
    proxy: {
      '/api': {
        // КРИТИЧЕСКИ ВАЖНО:
        // Внутри Docker-сети мы перенаправляем запросы на имя сервиса "backend" и его внутренний порт "8000"
        target: 'http://backend:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})