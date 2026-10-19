export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore()

  // Initialize store from cookies (Universal - Works on Server and Client)
  authStore.init()

  const isLoginPage = to.path === '/login'

  // If not authenticated and not on login page, redirect to login
  if (!authStore.isAuthenticated && !isLoginPage) {
    return navigateTo('/login')
  }

  // If authenticated and on login page, redirect to home
  if (authStore.isAuthenticated && isLoginPage) {
    return navigateTo('/')
  }
})
