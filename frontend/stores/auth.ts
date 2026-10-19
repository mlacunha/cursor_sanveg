import { defineStore } from 'pinia'
import { useApi } from '~/composables/useApi'

interface User {
  id: string
  login: string
  nome: string
  email: string
  role: string
  [key: string]: any
}

interface AuthState {
  token: string | null
  user: User | null
  loading: boolean
  error: string | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: null,
    user: null,
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
  },

  actions: {
    async login(credentials: { email: string; password: string }) {
      this.loading = true
      this.error = null

      try {
        const api = useApi()
        const response = await api<any>(`/api/auth/login`, {
          method: 'POST',
          body: credentials,
        })

        // Persistence using cookies (SSR-friendly)
        const tokenCookie = useCookie('token', { maxAge: 60 * 60 * 24 * 7 })
        const userCookie = useCookie<User | null>('user', { maxAge: 60 * 60 * 24 * 7 })

        this.token = response.access_token
        this.user = response.user
        
        tokenCookie.value = this.token
        userCookie.value = this.user

        return true
      } catch (err: any) {
        console.error('Login error:', err)
        this.error = err.data?.detail || 'Erro ao conectar com o servidor.'
        return false
      } finally {
        this.loading = false
      }
    },

    logout() {
      const tokenCookie = useCookie('token')
      const userCookie = useCookie('user')
      
      this.token = null
      this.user = null
      tokenCookie.value = null
      userCookie.value = null
      
      return navigateTo('/login')
    },

    init() {
      const tokenCookie = useCookie('token')
      const userCookie = useCookie<User | null>('user')

      if (tokenCookie.value) {
        this.token = tokenCookie.value
      }
      
      if (userCookie.value) {
        this.user = userCookie.value
      }
    }
  }
})
