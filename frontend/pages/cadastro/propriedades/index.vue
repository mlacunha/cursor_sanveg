<template>
  <div class="space-y-6">
    <!-- Componente Principal de Tabela -->
    <BaseDataTable
      title="Propriedades Rurais"
      subtitle="Gerencie e pesquise as propriedades rurais cadastradas localmente"
      :columns="columns"
      :items="items"
      :loading="loading"
      search-placeholder="Buscar propriedade por nome ou município..."
      show-add-button
      add-label="Nova Propriedade"
      show-row-actions
      @add="navigateToAdd"
      @edit="navigateToEdit"
      @delete="confirmDelete"
    >
      <!-- Customização das Colunas -->
      <template #col-produtor_nome="{ item }">
        <span class="font-medium text-gray-700 dark:text-gray-300">
          {{ item.produtor_nome || 'Não associado' }}
        </span>
      </template>
    </BaseDataTable>

    <!-- Modal de Confirmação de Exclusão -->
    <BaseModal
      v-if="showDeleteModal"
      title="Confirmar Exclusão"
      @close="showDeleteModal = false"
    >
      <div class="space-y-4">
        <p class="text-sm text-gray-600 dark:text-gray-300">
          Tem certeza que deseja excluir a propriedade <span class="font-bold text-gray-800 dark:text-white">{{ selectedItem?.nome }}</span>?
        </p>
        <p class="text-xs text-amber-600 bg-amber-50 dark:bg-amber-950/20 px-3 py-2 rounded-lg border border-amber-100 dark:border-amber-900/50">
          A exclusão será registrada localmente e sincronizada com o servidor quando estiver online.
        </p>
        
        <div class="flex justify-end gap-3 pt-2">
          <BaseButton variant="ghost" @click="showDeleteModal = false">
            Cancelar
          </BaseButton>
          <BaseButton variant="danger" @click="handleDelete">
            Confirmar Exclusão
          </BaseButton>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { db, type Propriedade, offlineDelete } from '~/utils/db'

const items = ref<any[]>([])
const loading = ref(false)
const showDeleteModal = ref(false)
const selectedItem = ref<Propriedade | null>(null)

// Configuração das colunas da tabela de propriedades
const columns = [
  { key: 'nome', label: 'Nome da Propriedade' },
  { key: 'municipio', label: 'Município' },
  { key: 'produtor_nome', label: 'Produtor Responsável' },
  { key: 'car_numero', label: 'Cadastro Ambiental Rural (CAR)' }
]

// Carrega os dados locais com associação produtores em memória
const loadData = async () => {
  if (process.client && db) {
    loading.value = true
    try {
      // Busca produtores para mapeamento rápido de nomes
      const producers = await db.produtores.toArray()
      const producersMap = new Map<string, string>()
      producers.forEach(p => {
        if (p.id) producersMap.set(p.id, p.nome || '')
      })

      // Busca propriedades rurais
      const properties = await db.propriedades.toArray()
      
      // Associa em tempo de execução
      items.value = properties.map(prop => ({
        ...prop,
        produtor_nome: producersMap.get(String(prop.id_produtor)) || producersMap.get(String(prop.produtor_id)) || 'Não associado'
      }))
    } catch (err) {
      console.error('[Propriedades] Erro ao buscar dados locais:', err)
    } finally {
      loading.value = false
    }
  }
}

onMounted(() => {
  loadData()
})

// Navegação para rotas
const navigateToAdd = () => {
  navigateTo('/cadastro/propriedades/novo')
}

const navigateToEdit = (item: Propriedade) => {
  navigateTo(`/cadastro/propriedades/${item.id}`)
}

// Fluxo de deleção
const confirmDelete = (item: Propriedade) => {
  selectedItem.value = item
  showDeleteModal.value = true
}

const handleDelete = async () => {
  if (selectedItem.value && process.client && db) {
    try {
      // Exclui localmente e enfileira na syncQueue
      await offlineDelete('propriedades', selectedItem.value.id)
      showDeleteModal.value = false
      selectedItem.value = null
      
      // Recarrega listagem
      await loadData()
    } catch (err) {
      console.error('[Propriedades] Erro ao deletar registro:', err)
    }
  }
}
</script>
