import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// Plugin personalizado para CORS — garantiza headers en TODAS las respuestas
function corsPlugin() {
  return {
    name: 'cors-middleware',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        const allowedOrigins = [
          'https://mirofish-tan.vercel.app',
          'https://mirofish.vercel.app',
          'http://localhost:5173',
          'http://localhost:3000',
          'http://127.0.0.1:5173',
          'http://127.0.0.1:3000',
        ]
        const origin = req.headers.origin || ''
        if (allowedOrigins.includes(origin) || origin) {
          res.setHeader('Access-Control-Allow-Origin', origin)
        }
        res.setHeader('Access-Control-Allow-Credentials', 'true')
        res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH')
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Accept')
        res.setHeader('Access-Control-Max-Age', '86400')

        // Responder inmediatamente a preflight OPTIONS
        if (req.method === 'OPTIONS') {
          res.statusCode = 204
          res.end()
          return
        }

        next()
      })
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), corsPlugin()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@locales': path.resolve(__dirname, '../locales')
    }
  },
  server: {
    port: 3000,
    open: true,
    allowedHosts: ['.onrender.com', 'localhost', '.vercel.app'],
    // CORS nativo de Vite — maneja OPTIONS antes que mi plugin
    cors: {
      origin: ['https://mirofish-tan.vercel.app', 'https://mirofish.vercel.app', 'http://localhost:5173', 'http://localhost:3000'],
      credentials: true,
      methods: 'GET,POST,PUT,DELETE,OPTIONS,PATCH',
      allowedHeaders: 'Content-Type,Authorization,X-Requested-With,Accept',
    },
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false
      },
      '/health': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
