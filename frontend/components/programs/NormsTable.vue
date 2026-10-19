<template>
  <div class="overflow-x-auto">
    <!-- Search Bar -->
    <div class="p-4 border-b border-gray-100 dark:border-gray-800 flex items-center">
      <div class="relative w-full max-w-xs">
        <Icon name="lucide:search" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar norma..."
          class="pl-10 pr-4 py-2 w-full bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all"
        />
      </div>
    </div>

    <table class="w-full text-left border-collapse">
      <thead>
        <tr class="border-b border-gray-100 dark:border-gray-800">
          <th class="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Norma / Legislação</th>
          <th class="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Tipo</th>
          <th class="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Data</th>
          <th class="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider text-right">Ações</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-50 dark:divide-gray-800">
        <tr v-for="norm in filteredNorms" :key="norm.id" class="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors group">
          <td class="px-6 py-4">
            <div class="flex flex-col">
              <span class="font-bold text-gray-900 dark:text-white">{{ norm.numero }}</span>
              <span class="text-sm text-gray-500">{{ norm.ementa }}</span>
            </div>
          </td>
          <td class="px-6 py-4">
            <span class="px-2 py-1 text-[10px] font-bold uppercase rounded-md bg-blue-50 text-[#1714EF] border border-blue-100">
              {{ norm.tipo }}
            </span>
          </td>
          <td class="px-6 py-4 text-sm text-gray-500">
            {{ norm.data }}
          </td>
          <td class="px-6 py-4 text-right">
            <div class="flex items-center justify-end gap-3">
              <!-- Ver PDF (Sutil) -->
              <BaseButton 
                variant="ghost"
                size="sm"
                icon="lucide:file-text"
                class="!text-slate-400 hover:!text-[#1714EF] !px-2"
                title="Ver PDF"
              >
                Ver PDF
              </BaseButton>

              <div class="h-4 w-[1px] bg-gray-100 dark:bg-gray-700 mx-1"></div>

              <!-- Editar -->
              <BaseButton 
                variant="ghost"
                size="icon"
                icon="lucide:edit"
                class="text-slate-400 hover:text-[#1714EF] hover:bg-blue-50"
                title="Editar"
              />

              <!-- Excluir -->
              <BaseButton 
                variant="ghost"
                size="icon"
                icon="lucide:trash-2"
                class="text-slate-400 hover:text-red-500 hover:bg-red-50"
                title="Excluir"
              />
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Empty State -->
    <div v-if="filteredNorms.length === 0" class="p-12 text-center text-gray-500">
      <p>{{ searchQuery ? 'Nenhuma norma encontrada para esta busca.' : 'Nenhuma norma vinculada a este programa.' }}</p>
    </div>

    <div class="p-4 border-t border-gray-100 dark:border-gray-800 flex justify-center">
      <BaseButton 
        variant="primary"
        icon="lucide:plus-circle"
        @click="$emit('add')"
      >
        Vincular Nova Norma
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Norm {
  id: string
  numero: string
  ementa: string
  tipo: string
  data: string
}

const props = defineProps<{
  norms: Norm[]
}>()

const searchQuery = ref('')

const filteredNorms = computed(() => {
  if (!searchQuery.value) return props.norms
  
  const query = searchQuery.value.toLowerCase()
  return props.norms.filter(n => 
    n.numero.toLowerCase().includes(query) || 
    n.ementa.toLowerCase().includes(query)
  )
})
</script>
