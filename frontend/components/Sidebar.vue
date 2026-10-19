<template>
  <aside
    class="fixed inset-y-0 left-0 z-50 lg:z-auto lg:static h-screen border-r border-gray-200 bg-white dark:bg-slate-900 dark:border-gray-800 transition-all duration-500 ease-in-out transform shadow-2xl lg:shadow-none"
    :class="[
      isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
      isSidebarCollapsed ? 'lg:w-20' : 'lg:w-64 w-64'
    ]"
    aria-label="Sidebar"
  >
    <div class="h-full flex flex-col px-4 py-6 overflow-y-auto">
      <!-- Logo / App Name & Collapse Toggle -->
      <div class="flex items-center justify-between px-2 mb-10 overflow-hidden">
        <div class="flex items-center min-w-0">
          <div class="w-9 h-9 bg-[#1714EF] rounded-lg flex-shrink-0 flex items-center justify-center mr-3 shadow-md shadow-blue-500/20">
            <Icon name="lucide:leaf" class="text-white text-xl" />
          </div>
          <div v-if="!isSidebarCollapsed" class="flex flex-col whitespace-nowrap transition-opacity duration-300">
            <span class="text-lg font-bold tracking-tight text-gray-900 dark:text-white leading-tight">
              SVEG<span class="text-[#1714EF]">PA</span>
            </span>
            <span class="text-[10px] text-gray-400 font-medium tracking-widest uppercase">Sistema de Pessoas</span>
          </div>
        </div>
        
        <!-- Desktop Collapse Button -->
        <BaseButton 
          variant="ghost" 
          size="icon" 
          class="hidden lg:flex transition-transform duration-300"
          :class="isSidebarCollapsed ? 'rotate-180 ml-auto' : ''"
          @click="toggleCollapse"
        >
          <Icon name="lucide:chevron-left" class="w-5 h-5 text-gray-400" />
        </BaseButton>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 space-y-1">
        <!-- Grupo Programas (Accordion) -->
        <div class="space-y-1">
          <BaseButton 
            variant="ghost"
            class="w-full !px-4 !py-3 !text-sm !font-bold text-gray-700 dark:text-gray-200 !rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-all group !justify-start"
            :title="isSidebarCollapsed ? 'Programas' : ''"
            @click="submenus.programas = !submenus.programas"
          >
            <div class="flex items-center justify-between w-full overflow-hidden">
              <div class="flex items-center flex-1 min-w-0">
                <Icon name="lucide:layers" class="w-5 h-5 mr-3 text-[#1714EF] flex-shrink-0" />
                <span v-if="!isSidebarCollapsed" class="flex-1 text-left whitespace-nowrap overflow-hidden text-ellipsis">Programas</span>
              </div>
              <Icon 
                v-if="!isSidebarCollapsed"
                name="lucide:chevron-down" 
                class="w-4 h-4 transition-transform duration-200 flex-shrink-0 ml-auto"
                :class="{ 'rotate-180': submenus.programas }"
              />
            </div>
          </BaseButton>
          
          <div v-show="submenus.programas && !isSidebarCollapsed" class="space-y-1 ml-4 border-l-2 border-gray-100 dark:border-gray-800 pl-2 transition-all">
            <NuxtLink to="/cadastro/programas" class="flex items-center px-4 py-2.5 text-sm font-medium text-gray-600 rounded-lg hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors group" active-class="!bg-blue-50 !text-[#1714EF] dark:!bg-blue-900/20" @click="closeSidebar">
              <Icon name="lucide:layout-list" class="w-4 h-4 mr-3 flex-shrink-0" />
              <span>Gerenciar Programas</span>
            </NuxtLink>
            
            <NuxtLink to="/cadastro/hospedeiros" class="flex items-center px-4 py-2.5 text-sm font-medium text-gray-600 rounded-lg hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors group" active-class="!bg-blue-50 !text-[#1714EF] dark:!bg-blue-900/20" @click="closeSidebar">
              <Icon name="lucide:leaf" class="w-4 h-4 mr-3 flex-shrink-0" />
              <span>Hospedeiros</span>
            </NuxtLink>
            
            <NuxtLink to="/cadastro/normas" class="flex items-center px-4 py-2.5 text-sm font-medium text-gray-600 rounded-lg hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors group" active-class="!bg-blue-50 !text-[#1714EF] dark:!bg-blue-900/20" @click="closeSidebar">
              <Icon name="lucide:scroll-text" class="w-4 h-4 mr-3 flex-shrink-0" />
              <span>Normas e Legislação</span>
            </NuxtLink>
          </div>
        </div>

        <!-- Grupo Cadastros (Accordion) -->
        <div class="space-y-1">
          <BaseButton 
            variant="ghost"
            class="w-full !px-4 !py-3 !text-sm !font-bold text-gray-700 dark:text-gray-200 !rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-all group !justify-start"
            :title="isSidebarCollapsed ? 'Cadastros' : ''"
            @click="submenus.cadastros = !submenus.cadastros"
          >
            <div class="flex items-center justify-between w-full overflow-hidden">
              <div class="flex items-center flex-1 min-w-0">
                <Icon name="lucide:clipboard-list" class="w-5 h-5 mr-3 text-[#1714EF] flex-shrink-0" />
                <span v-if="!isSidebarCollapsed" class="flex-1 text-left whitespace-nowrap overflow-hidden text-ellipsis">Cadastros</span>
              </div>
              <Icon 
                v-if="!isSidebarCollapsed"
                name="lucide:chevron-down" 
                class="w-4 h-4 transition-transform duration-200 flex-shrink-0 ml-auto"
                :class="{ 'rotate-180': submenus.cadastros }"
              />
            </div>
          </BaseButton>
          
          <div v-show="submenus.cadastros && !isSidebarCollapsed" class="space-y-1 ml-4 border-l-2 border-gray-100 dark:border-gray-800 pl-2 transition-all">
            <NuxtLink to="/cadastro/produtores" class="flex items-center px-4 py-2.5 text-sm font-medium text-gray-600 rounded-lg hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors group" active-class="!bg-blue-50 !text-[#1714EF] dark:!bg-blue-900/20" @click="closeSidebar">
              <Icon name="lucide:users" class="w-4 h-4 mr-3 flex-shrink-0" />
              <span>Produtores</span>
            </NuxtLink>
            
            <NuxtLink to="/cadastro/propriedades" class="flex items-center px-4 py-2.5 text-sm font-medium text-gray-600 rounded-lg hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors group" active-class="!bg-blue-50 !text-[#1714EF] dark:!bg-blue-900/20" @click="closeSidebar">
              <Icon name="lucide:home" class="w-4 h-4 mr-3 flex-shrink-0" />
              <span>Propriedades</span>
            </NuxtLink>
          </div>
        </div>

        <!-- Grupo Fiscalização (Accordion) -->
        <div class="space-y-1">
          <BaseButton 
            variant="ghost"
            class="w-full !px-4 !py-3 !text-sm !font-bold text-gray-700 dark:text-gray-200 !rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-all group !justify-start"
            :title="isSidebarCollapsed ? 'Fiscalização' : ''"
            @click="submenus.fiscalizacao = !submenus.fiscalizacao"
          >
            <div class="flex items-center justify-between w-full overflow-hidden">
              <div class="flex items-center flex-1 min-w-0">
                <Icon name="lucide:shield" class="w-5 h-5 mr-3 text-[#1714EF] flex-shrink-0" />
                <span v-if="!isSidebarCollapsed" class="flex-1 text-left whitespace-nowrap overflow-hidden text-ellipsis">Fiscalização</span>
              </div>
              <Icon 
                v-if="!isSidebarCollapsed"
                name="lucide:chevron-down" 
                class="w-4 h-4 transition-transform duration-200 flex-shrink-0 ml-auto"
                :class="{ 'rotate-180': submenus.fiscalizacao }"
              />
            </div>
          </BaseButton>
          
          <div v-show="submenus.fiscalizacao && !isSidebarCollapsed" class="space-y-1 ml-4 border-l-2 border-gray-100 dark:border-gray-800 pl-2 transition-all">
            <NuxtLink to="/inspecoes" class="flex items-center px-4 py-2.5 text-sm font-medium text-gray-600 rounded-lg hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors group" active-class="!bg-blue-50 !text-[#1714EF] dark:!bg-blue-900/20" @click="closeSidebar">
              <Icon name="lucide:clipboard-check" class="w-4 h-4 mr-3 flex-shrink-0" />
              <span>Inspeções</span>
            </NuxtLink>
            
            <NuxtLink to="/relatorios/mapas" class="flex items-center px-4 py-2.5 text-sm font-medium text-gray-600 rounded-lg hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors group" active-class="!bg-blue-50 !text-[#1714EF] dark:!bg-blue-900/20" @click="closeSidebar">
              <Icon name="lucide:map" class="w-4 h-4 mr-3 flex-shrink-0" />
              <span>Mapa de Ocorrências</span>
            </NuxtLink>
          </div>
        </div>

        <!-- Grupo Administração (Accordion) -->
        <div class="space-y-1">
          <BaseButton 
            variant="ghost"
            class="w-full !px-4 !py-3 !text-sm !font-bold text-gray-700 dark:text-gray-200 !rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-all group !justify-start"
            :title="isSidebarCollapsed ? 'Administração' : ''"
            @click="submenus.administracao = !submenus.administracao"
          >
            <div class="flex items-center justify-between w-full overflow-hidden">
              <div class="flex items-center flex-1 min-w-0">
                <Icon name="lucide:settings" class="w-5 h-5 mr-3 text-[#1714EF] flex-shrink-0" />
                <span v-if="!isSidebarCollapsed" class="flex-1 text-left whitespace-nowrap overflow-hidden text-ellipsis">Administração</span>
              </div>
              <Icon 
                v-if="!isSidebarCollapsed"
                name="lucide:chevron-down" 
                class="w-4 h-4 transition-transform duration-200 flex-shrink-0 ml-auto"
                :class="{ 'rotate-180': submenus.administracao }"
              />
            </div>
          </BaseButton>
          
          <div v-show="submenus.administracao && !isSidebarCollapsed" class="space-y-1 ml-4 border-l-2 border-gray-100 dark:border-gray-800 pl-2 transition-all">
            <NuxtLink to="/usuarios" class="flex items-center px-4 py-2.5 text-sm font-medium text-gray-600 rounded-lg hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-800 transition-colors group" active-class="!bg-blue-50 !text-[#1714EF] dark:!bg-blue-900/20" @click="closeSidebar">
              <Icon name="lucide:users" class="w-4 h-4 mr-3 flex-shrink-0" />
              <span>Usuários</span>
            </NuxtLink>
          </div>
        </div>
      </nav>

      <!-- User / Logout -->
      <div class="mt-auto pt-6 border-t border-gray-100 dark:border-gray-800">
        <div class="flex items-center px-2 mb-4 overflow-hidden">
          <div class="w-9 h-9 flex-shrink-0 rounded-full bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center text-[#1714EF] font-bold">
            {{ (authStore.user?.nome || 'U').charAt(0).toUpperCase() }}
          </div>
          <div v-if="!isSidebarCollapsed" class="ml-3 min-w-0 transition-opacity duration-300">
            <p class="text-sm font-semibold text-gray-900 dark:text-white truncate">
              {{ authStore.user?.nome || 'Usuário' }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400 truncate">
              {{ authStore.user?.email || 'admin@admin.com' }}
            </p>
          </div>
        </div>
        <BaseButton
          variant="ghost"
          icon="lucide:log-out"
          class="w-full !justify-start !text-red-600 hover:!bg-red-50 dark:hover:!bg-red-900/20"
          :title="isSidebarCollapsed ? 'Sair' : ''"
          @click="authStore.logout()"
        >
          <span v-if="!isSidebarCollapsed">Sair</span>
        </BaseButton>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
const { isSidebarOpen, isSidebarCollapsed, closeSidebar, toggleCollapse } = useUI()

const submenus = reactive({
  programas: true,
  cadastros: true,
  fiscalizacao: true,
  administracao: true
})

const toggleSubmenu = (menu: keyof typeof submenus) => {
  submenus[menu] = !submenus[menu]
}
</script>
