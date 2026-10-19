<template>
  <div class="flex min-h-screen bg-slate-50 relative">
    <!-- Overlay Backdrop (Mobile) -->
    <div 
      v-if="isSidebarOpen" 
      class="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm lg:hidden transition-opacity"
      @click="closeSidebar"
    ></div>

    <!-- Sidebar component with internal state handling -->
    <Sidebar />
    
    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col min-h-screen min-w-0">
      <AppHeader />
      
      <main class="flex-1 overflow-y-auto p-4 md:p-8">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const { isSidebarOpen, closeSidebar } = useUI()
</script>

<style>
/* Global layout scrollbar styling */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}

.dark ::-webkit-scrollbar-thumb {
  background: #1e293b;
}

::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style>
