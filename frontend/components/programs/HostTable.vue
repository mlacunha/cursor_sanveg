<template>
  <div class="overflow-x-auto">
    <!-- Search Bar -->
    <div class="p-4 border-b border-gray-100 dark:border-gray-800 flex items-center">
      <div class="relative w-full max-w-xs">
        <Icon name="lucide:search" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar hospedeiro..."
          class="pl-10 pr-4 py-2 w-full bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all"
        />
      </div>
    </div>

    <table class="w-full text-left border-collapse">
      <thead>
        <tr class="border-b border-gray-100 dark:border-gray-800">
          <th class="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Hospedeiro</th>
          <th class="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Nome Científico</th>
          <th class="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider text-right">Ações</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-50 dark:divide-gray-800">
        <tr v-for="host in filteredHosts" :key="host.id" class="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors group">
          <td class="px-6 py-4">
            <span class="font-medium text-gray-900 dark:text-white">{{ host.nome }}</span>
          </td>
          <td class="px-6 py-4">
            <span class="italic text-brand-blue font-medium">{{ host.nome_cientifico }}</span>
          </td>
          <td class="px-6 py-4 text-right">
            <div class="flex items-center justify-end gap-2">
              <BaseButton 
                variant="ghost"
                size="icon"
                icon="lucide:edit"
                class="text-slate-400 hover:text-[#1714EF] hover:bg-blue-50"
                title="Editar"
              />
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

    <!-- Empty State / Add Action -->
    <div v-if="filteredHosts.length === 0" class="p-12 text-center">
      <p class="text-gray-500 mb-4">
        {{ searchQuery ? 'Nenhum hospedeiro encontrado para esta busca.' : 'Nenhum hospedeiro vinculado a este programa.' }}
      </p>
    </div>
    
    <div class="p-4 border-t border-gray-100 dark:border-gray-800 flex justify-center">
      <BaseButton 
        variant="primary"
        icon="lucide:plus-circle"
        @click="$emit('add')"
      >
        Vincular Novo Hospedeiro
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Host {
  id: string
  nome: string
  nome_cientifico: string
}

const props = defineProps<{
  hosts: Host[]
}>()

const searchQuery = ref('')

const filteredHosts = computed(() => {
  if (!searchQuery.value) return props.hosts
  
  const query = searchQuery.value.toLowerCase()
  return props.hosts.filter(h => 
    h.nome.toLowerCase().includes(query) || 
    h.nome_cientifico.toLowerCase().includes(query)
  )
})
</script>

<style scoped>
.text-brand-blue {
  color: #1714EF;
}
</style>
