import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  define: {
    'process.env.APP_VERSION': JSON.stringify(process.env.npm_package_version),
  },
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    include: ['src/__tests__/**/*.{test,spec}.{js,jsx}'],
    passWithNoTests: true,
    setupFiles: 'src/tests/setup.js',
  },
})
