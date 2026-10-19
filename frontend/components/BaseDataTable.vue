<template>
  <div class="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 overflow-hidden">
    <!-- Header -->
    <div class="p-6 border-b border-gray-100 dark:border-gray-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 dark:text-white">{{ title }}</h1>
        <p v-if="subtitle" class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ subtitle }}</p>
      </div>
      
      <div class="flex items-center gap-3">
        <!-- Search -->
        <div class="relative">
          <Icon name="lucide:search" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="searchPlaceholder || 'Buscar...'"
            class="pl-10 pr-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue outline-none transition-all w-full md:w-64"
          />
        </div>
        
        <!-- Actions -->
        <slot name="actions"></slot>
        
        <BaseButton
          v-if="showAddButton"
          variant="primary"
          icon="lucide:plus"
          @click="$emit('add')"
        >
          {{ addLabel || 'Novo' }}
        </BaseButton>
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-gray-50/50 dark:bg-gray-800/50">
            <th
              v-for="col in columns"
              :key="col.key"
              class="px-6 py-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
              :class="col.class"
            >
              {{ col.label }}
            </th>
            <th v-if="showRowActions" class="px-6 py-4 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider text-right">
              Ações
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
          <tr v-if="loading">
            <td :colspan="columns.length + (showRowActions ? 1 : 0)" class="px-6 py-12 text-center text-gray-500">
              <div class="flex flex-col items-center gap-3">
                <div class="w-8 h-8 border-4 border-[#1714EF] border-t-transparent rounded-full animate-spin"></div>
                <span class="text-sm font-medium">Carregando dados...</span>
              </div>
            </td>
          </tr>
          
          <tr v-else-if="filteredItems.length === 0">
            <td :colspan="columns.length + (showRowActions ? 1 : 0)" class="px-6 py-12 text-center text-gray-500">
              <div class="flex flex-col items-center gap-2">
                <Icon name="lucide:folder-open" class="w-10 h-10 text-gray-300 mb-2" />
                <span class="text-sm font-medium">Nenhum registro encontrado</span>
              </div>
            </td>
          </tr>
          
          <tr
            v-else
            v-for="(item, index) in filteredItems"
            :key="item.id || index"
            class="hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors group"
          >
            <td
              v-for="col in columns"
              :key="col.key"
              class="px-6 py-4 text-sm text-gray-700 dark:text-gray-300"
              :class="col.class"
            >
              <slot :name="`col-${col.key}`" :item="item" :value="item[col.key]">
                <span :class="{ 'italic': col.isScientific || col.key === 'nome_cientifico' }">
                  {{ item[col.key] || '-' }}
                </span>
              </slot>
            </td>
            
            <td v-if="showRowActions" class="px-8 py-4 text-right">
              <div class="flex items-center justify-end gap-3 transition-opacity">
                <BaseButton
                  variant="ghost"
                  size="icon"
                  icon="lucide:edit-2"
                  class="text-slate-400 hover:text-[#1714EF]"
                  title="Editar"
                  @click="$emit('edit', item)"
                />
                <BaseButton
                  variant="ghost"
                  size="icon"
                  icon="lucide:trash-2"
                  class="text-slate-400 hover:text-red-500"
                  title="Excluir"
                  @click="$emit('delete', item)"
                />
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Footer / Pagination -->
    <div class="p-4 border-t border-gray-100 dark:border-gray-800 bg-gray-50/30 dark:bg-gray-800/20 flex items-center justify-between">
      <span class="text-xs text-gray-500 dark:text-gray-400">
        Mostrando {{ filteredItems.length }} de {{ items.length }} registros
      </span>
      <div class="flex items-center gap-2">
        <!-- Add internal pagination here if needed -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Column {
  key: string
  label: string
  class?: string
  isScientific?: boolean
}

const props = defineProps<{
  title: string
  subtitle?: string
  columns: Column[]
  items: any[]
  loading?: boolean
  searchPlaceholder?: string
  showAddButton?: boolean
  addLabel?: string
  showRowActions?: boolean
}>()

const emit = defineEmits(['add', 'edit', 'delete'])

const searchQuery = ref('')

const filteredItems = computed(() => {
  if (!searchQuery.value) return props.items
  
  const query = searchQuery.value.toLowerCase()
  return props.items.filter(item => {
    return props.columns.some(col => {
      const value = item[col.key]
      return value && String(value).toLowerCase().includes(query)
    })
  })
})
</script>
