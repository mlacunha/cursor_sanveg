<template>
  <header class="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-gray-200 bg-white/80 px-8 backdrop-blur-md dark:border-gray-800 dark:bg-slate-900/80">
    <div class="flex items-center gap-4">
      <!-- Hamburger Menu (Mobile/Tablet) -->
      <BaseButton 
        variant="ghost" 
        size="icon"
        class="lg:hidden text-gray-500"
        @click="toggleSidebar"
      >
        <Icon name="lucide:menu" class="w-6 h-6" />
      </BaseButton>

      <!-- Breadcrumb / Title -->
      <h1 class="text-lg font-bold text-gray-800 dark:text-white">
        {{ pageTitle }}
      </h1>
    </div>

    <div class="flex items-center gap-6">
      <!-- Sync Status (Real Offline Engine) -->
      <SyncManager />

      <!-- Theme Toggle (Simplified for now) -->
      <BaseButton 
        variant="ghost" 
        size="icon"
        class="text-gray-500"
        @click="isDark = !isDark"
      >
        <Icon :name="isDark ? 'lucide:sun' : 'lucide:moon'" class="w-5 h-5" />
      </BaseButton>

      <!-- Notifications -->
      <BaseButton 
        variant="ghost" 
        size="icon"
        class="text-gray-500"
      >
        <Icon name="lucide:bell" class="w-5 h-5" />
        <span class="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-slate-900"></span>
      </BaseButton>
    </div>
  </header>
</template>

<script setup lang="ts">
const route = useRoute()
const { toggleSidebar } = useUI()

const isDark = ref(false)

const pageTitle = computed(() => {
  const path = route.path
  if (path === '/') return 'Principal'
  if (path.startsWith('/mapas')) return 'Mapas Espaciais'
  if (path.startsWith('/cadastro/produtores')) return 'Cadastro de Produtores'
  if (path.startsWith('/cadastro/propriedades')) return 'Cadastro de Propriedades'
  if (path.startsWith('/cadastro/programas')) return 'Programas Fitossanitários'
  if (path.startsWith('/cadastro/hospedeiros')) return 'Hospedeiros Vegetais'
  if (path.startsWith('/cadastro/normas')) return 'Normas e Legislação'
  if (path.startsWith('/levantamentos')) return 'Levantamentos de Campo'
  if (path.startsWith('/relatorios')) return 'Relatórios e Estatísticas'
  return 'SVEGPA'
})
</script>

<style scoped>
.animate-spin-slow {
  animation: spin 3s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
