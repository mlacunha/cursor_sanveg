export const useApi = () => {
  const config = useRuntimeConfig()
  const baseUrl = config.public.apiBase || 'http://localhost:8000'

  return $fetch.create({
    baseURL: baseUrl,
    async onRequest({ options }) {
      const auth = useAuthStore()
      if (auth.token) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${auth.token}`
        }
      }
    },
    async onResponseError({ response }) {
      const auth = useAuthStore()
      if (response.status === 401) {
        auth.logout()
      }
    }
  })
}

