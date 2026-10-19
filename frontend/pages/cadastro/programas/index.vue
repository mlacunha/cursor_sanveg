<template>
  <div class="space-y-6">
    <BaseDataTable
      title="Programas"
      subtitle="Gerencie os programas fitossanitários do sistema"
      :columns="columns"
      :items="programas"
      :loading="loading"
      show-add-button
      show-row-actions
      add-label="Novo Programa"
      @add="openCreateModal"
      @edit="goToDetail"
      @delete="confirmDelete"
    />

    <!-- Create/Edit Modal -->
    <BaseModal
      :show="showModal"
      :title="isEditing ? 'Editar Programa' : 'Novo Programa'"
      :confirm-label="isEditing ? 'Salvar Alterações' : 'Criar Programa'"
      :loading="submitting"
      @close="closeModal"
      @confirm="savePrograma"
    >
      <form class="space-y-4" @submit.prevent="savePrograma">
        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Código</label>
          <input
            v-model="form.codigo"
            type="text"
            placeholder="Ex: PNVF"
            class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all"
          />
        </div>
        
        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Nome *</label>
          <input
            v-model="form.nome"
            type="text"
            required
            placeholder="Ex: Programa Nacional de Vigilância Fitossanitária"
            class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Nomes Comuns</label>
          <input
            v-model="form.nomes_comuns"
            type="text"
            placeholder="Ex: Pragas das Frutas"
            class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Nome Científico</label>
          <input
            v-model="form.nome_cientifico"
            type="text"
            placeholder="Ex: Candidatus Liberibacter"
            class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all italic"
          />
        </div>
      </form>
    </BaseModal>

    <!-- Delete Confirmation Modal -->
    <BaseModal
      :show="showDeleteModal"
      title="Excluir Programa"
      confirm-label="Excluir"
      :loading="submitting"
      class="delete-modal"
      @close="showDeleteModal = false"
      @confirm="deletePrograma"
    >
      <div class="flex flex-col items-center text-center py-4">
        <div class="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center text-red-500 mb-4">
          <Icon name="lucide:alert-triangle" class="w-8 h-8" />
        </div>
        <p class="text-gray-700 dark:text-gray-300">
          Tem certeza que deseja excluir o programa <span class="font-bold text-gray-900 dark:text-white">{{ itemToDelete?.nome }}</span>?
        </p>
        <p class="text-sm text-gray-500 mt-2">Esta ação não pode ser desfeita.</p>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const loading = ref(false)
const submitting = ref(false)
const showModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const itemToDelete = ref(null)

// Dados Mockados para validação visual
const programas = ref([
  { 
    id: '1', 
    codigo: 'PNVF', 
    nome: 'Programa Nacional de Vigilância Fitossanitária', 
    nomes_comuns: 'Vigilância Geral, Monitoramento', 
    nome_cientifico: '-' 
  },
  { 
    id: '2', 
    codigo: 'HLB', 
    nome: 'Programa Estadual de Controle do HLB (Greening)', 
    nomes_comuns: 'Greening, Amarelão das Cítricas', 
    nome_cientifico: 'Candidatus Liberibacter' 
  },
  { 
    id: '3', 
    codigo: 'MF', 
    nome: 'Programa de Erradicação da Mosca das Frutas', 
    nomes_comuns: 'Mosca das Frutas, Bicho da Fruta', 
    nome_cientifico: 'Ceratitis capitata' 
  },
  { 
    id: '4', 
    codigo: 'CANO', 
    nome: 'Programa de Vigilância do Cancro Cítrico', 
    nomes_comuns: 'Cancro Cítrico', 
    nome_cientifico: 'Xanthomonas citri' 
  }
])

const columns = [
  { key: 'codigo', label: 'Código', class: 'w-24 font-bold text-brand-blue' },
  { key: 'nome', label: 'Nome', class: 'font-medium text-gray-900' },
  { key: 'nomes_comuns', label: 'Nomes Comuns', class: 'text-gray-500' },
  { key: 'nome_cientifico', label: 'Nome Científico', isScientific: true, class: 'italic text-gray-600' },
]

const submenus = reactive({
  cadastro: true
})

const form = reactive({
  id: '',
  codigo: '',
  nome: '',
  nomes_comuns: '',
  nome_cientifico: ''
})

const openCreateModal = () => {
  isEditing.value = false
  Object.assign(form, { id: '', codigo: '', nome: '', nomes_comuns: '', nome_cientifico: '' })
  showModal.value = true
}

const goToDetail = (item: any) => {
  navigateTo(`/cadastro/programas/${item.id}`)
}

const closeModal = () => {
  showModal.value = false
}

const savePrograma = async () => {
  if (!form.nome) return
  
  submitting.value = true
  // Simulação de delay para feedback visual do botão loading
  setTimeout(() => {
    const newId = String(Date.now())
    programas.value.push({
      ...form,
      id: newId
    })
    submitting.value = false
    closeModal()
    // Redireciona para a página de detalhes após a criação rápida
    navigateTo(`/cadastro/programas/${newId}`)
  }, 600)
}

const confirmDelete = (item: any) => {
  itemToDelete.value = item
  showDeleteModal.value = true
}

const deletePrograma = async () => {
  if (!itemToDelete.value) return
  
  submitting.value = true
  setTimeout(() => {
    programas.value = programas.value.filter(p => p.id !== itemToDelete.value.id)
    submitting.value = false
    showDeleteModal.value = false
  }, 400)
}
</script>
