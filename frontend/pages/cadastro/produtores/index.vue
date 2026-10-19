<template>
  <div class="space-y-6">
    <!-- Componente Principal de Tabela -->
    <BaseDataTable
      title="Produtores Agropecuários"
      subtitle="Gerencie e pesquise os produtores cadastrados localmente"
      :columns="columns"
      :items="items"
      :loading="loading"
      search-placeholder="Buscar produtor por nome ou CPF..."
      show-add-button
      add-label="Novo Produtor"
      show-row-actions
      @add="navigateToAdd"
      @edit="navigateToEdit"
      @delete="confirmDelete"
    >
      <!-- Customização de colunas se necessário -->
      <template #col-cpf_cnpj="{ item }">
        <span>{{ item.cpf_cnpj || item.cpf || item.cnpj || '-' }}</span>
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
          Tem certeza que deseja excluir o produtor <span class="font-bold text-gray-800 dark:text-white">{{ selectedItem?.nome }}</span>?
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
import { db, type Produtor } from '~/utils/db'

const items = ref<Produtor[]>([])
const loading = ref(false)
const showDeleteModal = ref(false)
const selectedItem = ref<Produtor | null>(null)

// Configuração das colunas da tabela
const columns = [
  { key: 'nome', label: 'Nome / Razão Social' },
  { key: 'cpf_cnpj', label: 'CPF / CNPJ' },
  { key: 'email', label: 'E-mail' },
  { key: 'telefone', label: 'Telefone' }
]

// Carrega os dados do Dexie local
const loadData = async () => {
  if (process.client && db) {
    loading.value = true
    try {
      items.value = await db.produtores.toArray()
    } catch (err) {
      console.error('[Produtores] Erro ao buscar dados locais:', err)
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
  navigateTo('/cadastro/produtores/novo')
}

const navigateToEdit = (item: Produtor) => {
  navigateTo(`/cadastro/produtores/${item.id}`)
}

// Fluxo de deleção
const confirmDelete = (item: Produtor) => {
  selectedItem.value = item
  showDeleteModal.value = true
}

const handleDelete = async () => {
  if (selectedItem.value && process.client && db) {
    try {
      // Exclui localmente e enfileira na syncQueue
      await offlineDelete('produtores', selectedItem.value.id)
      showDeleteModal.value = false
      selectedItem.value = null
      
      // Recarrega listagem
      await loadData()
    } catch (err) {
      console.error('[Produtores] Erro ao deletar registro:', err)
    }
  }
}
</script>
