export const useUI = () => {
  const isSidebarOpen = useState('isSidebarOpen', () => false)
  const isSidebarCollapsed = useState('isSidebarCollapsed', () => false)

  const toggleSidebar = () => {
    isSidebarOpen.value = !isSidebarOpen.value
  }

  const closeSidebar = () => {
    isSidebarOpen.value = false
  }

  const openSidebar = () => {
    isSidebarOpen.value = true
  }

  const toggleCollapse = () => {
    isSidebarCollapsed.value = !isSidebarCollapsed.value
  }

  return {
    isSidebarOpen,
    isSidebarCollapsed,
    toggleSidebar,
    closeSidebar,
    openSidebar,
    toggleCollapse
  }
}
