import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig(({ mode }) => ({
  server: {
    port: 3000,

    // 🔥 Proxy vers ton backend en ClusterIP
    proxy: {
      '/quiz-info': {
        target: 'http://backend-service:3000',
        changeOrigin: true,
        secure: false,
      },
      // ajoute d'autres routes backend si nécessaire
      // '/api': { target: 'http://backend-service:3000', changeOrigin: true }
    },
  },

  plugins: [
    vue(),
    mode !== 'test' && vueDevTools(),
  ],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },

  test: {
    environment: 'jsdom',
  },
}))

