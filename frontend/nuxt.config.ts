// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  modules: [
    '@nuxtjs/tailwindcss',
    '@vite-pwa/nuxt',
    '@nuxt/icon',
    '@pinia/nuxt'
  ],

  runtimeConfig: {
    public: {
      apiBase: 'https://sanveg-api.vps5908.panel.icontainer.run'
    }
  },

  nitro: {
    routeRules: {
      '/api/**': { proxy: 'http://svegpa_api:8080/**' }
    }
  },

  vite: {
    server: {
      watch: {
        usePolling: true
      }
    }
  },

  pwa: {
    manifest: {
      name: 'SVEGPA - Sanidade Vegetal',
      short_name: 'SVEGPA',
      description: 'Sistema de Vigilância Epidemiológica e Gestão de Pragas Agrícolas',
      theme_color: '#1714EF',
      lang: 'pt-BR',
      icons: [
        {
          src: 'pwa-192x192.png',
          sizes: '192x192',
          type: 'image/png'
        },
        {
          src: 'pwa-512x512.png',
          sizes: '512x512',
          type: 'image/png'
        }
      ]
    }
  },

  icon: {
    provider: 'iconify'
  }
})
