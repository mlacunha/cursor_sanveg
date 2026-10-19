<template>
  <div class="space-y-6">
    <BaseDataTable
      title="Hospedeiros"
      subtitle="Gerencie as culturas e hospedeiros vinculados aos programas"
      :columns="columns"
      :items="hospedeiros"
      :loading="loading"
      show-add-button
      show-row-actions
      add-label="Novo Hospedeiro"
      @add="openCreateModal"
      @edit="openEditModal"
      @delete="confirmDelete"
    >
      <template #col-id_programa="{ item }">
        <span class="font-medium text-brand-blue">{{ item.programa?.nome || 'N/A' }}</span>
      </template>
    </BaseDataTable>

    <!-- Create/Edit Modal -->
    <BaseModal
      :show="showModal"
      :title="isEditing ? 'Editar Hospedeiro' : 'Novo Hospedeiro'"
      :confirm-label="isEditing ? 'Salvar Alterações' : 'Criar Hospedeiro'"
      :loading="submitting"
      @close="closeModal"
      @confirm="saveHospedeiro"
    >
      <form class="space-y-4" @submit.prevent="saveHospedeiro">
        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Programa Vinculado *</label>
          <select
            v-model="form.id_programa"
            required
            class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all"
          >
            <option value="" disabled>Selecione um programa</option>
            <option v-for="prog in programas" :key="prog.id" :value="prog.id">
              {{ prog.nome }}
            </option>
          </select>
        </div>
        
        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Nomes Comuns *</label>
          <input
            v-model="form.nomes_comuns"
            type="text"
            required
            placeholder="Ex: Soja, Milho"
            class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Nome Científico *</label>
          <input
            v-model="form.nome_cientifico"
            type="text"
            required
            placeholder="Ex: Glycine max"
            class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all italic"
          />
        </div>
      </form>
    </BaseModal>

    <!-- Delete Confirmation Modal -->
    <BaseModal
      :show="showDeleteModal"
      title="Excluir Hospedeiro"
      confirm-label="Excluir"
      :loading="submitting"
      @close="showDeleteModal = false"
      @confirm="deleteHospedeiro"
    >
      <div class="flex flex-col items-center text-center py-4">
        <div class="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center text-red-500 mb-4">
          <Icon name="lucide:alert-triangle" class="w-8 h-8" />
        </div>
        <p class="text-gray-700 dark:text-gray-300">
          Tem certeza que deseja excluir o hospedeiro <span class="font-bold text-gray-900 dark:text-white">{{ itemToDelete?.nomes_comuns }}</span>?
        </p>
        <p class="text-sm text-gray-500 mt-2">Esta ação não pode ser desfeita.</p>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const loading = ref(true)
const submitting = ref(false)
const hospedeiros = ref([])
const programas = ref([])
const showModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const itemToDelete = ref(null)

const columns = [
  { key: 'id_programa', label: 'Programa' },
  { key: 'nomes_comuns', label: 'Nomes Comuns' },
  { key: 'nome_cientifico', label: 'Nome Científico', isScientific: true },
]

const form = reactive({
  id: '',
  id_programa: '',
  nomes_comuns: '',
  nome_cientifico: ''
})

const fetchHospedeiros = async () => {
  loading.value = true
  try {
    hospedeiros.value = await api('/api/hospedeiros/')
  } catch (error) {
    console.error('Erro ao buscar hospedeiros:', error)
  } finally {
    loading.value = false
  }
}

const fetchProgramas = async () => {
  try {
    programas.value = await api('/api/programas/')
  } catch (error) {
    console.error('Erro ao buscar programas:', error)
  }
}

const openCreateModal = () => {
  isEditing.value = false
  Object.assign(form, { id: '', id_programa: '', nomes_comuns: '', nome_cientifico: '' })
  showModal.value = true
}

const openEditModal = (item: any) => {
  isEditing.value = true
  Object.assign(form, { ...item })
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const saveHospedeiro = async () => {
  if (!form.id_programa || !form.nomes_comuns || !form.nome_cientifico) return
  
  submitting.value = true
  try {
    if (isEditing.value) {
      await api(`/api/hospedeiros/${form.id}`, {
        method: 'PATCH',
        body: {
          id_programa: form.id_programa,
          nomes_comuns: form.nomes_comuns,
          nome_cientifico: form.nome_cientifico
        }
      })
    } else {
      await api('/api/hospedeiros/', {
        method: 'POST',
        body: {
          id_programa: form.id_programa,
          nomes_comuns: form.nomes_comuns,
          nome_cientifico: form.nome_cientifico
        }
      })
    }
    await fetchHospedeiros()
    closeModal()
  } catch (error) {
    console.error('Erro ao salvar hospedeiro:', error)
  } finally {
    submitting.value = false
  }
}

const confirmDelete = (item: any) => {
  itemToDelete.value = item
  showDeleteModal.value = true
}

const deleteHospedeiro = async () => {
  if (!itemToDelete.value) return
  
  submitting.value = true
  try {
    await api(`/api/hospedeiros/${itemToDelete.value.id}`, {
      method: 'DELETE'
    })
    await fetchHospedeiros()
    showDeleteModal.value = false
  } catch (error) {
    console.error('Erro ao excluir hospedeiro:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchHospedeiros()
  fetchProgramas()
})
</script>
