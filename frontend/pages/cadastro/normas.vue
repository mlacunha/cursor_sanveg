<template>
  <div class="space-y-6">
    <BaseDataTable
      title="Normas"
      subtitle="Cadastre as normas e legislações aplicáveis aos programas"
      :columns="columns"
      :items="normas"
      :loading="loading"
      show-add-button
      show-row-actions
      add-label="Nova Norma"
      @add="openCreateModal"
      @edit="openEditModal"
      @delete="confirmDelete"
    >
      <template #col-id_programa="{ item }">
        <span class="font-medium text-brand-blue">{{ item.programa?.nome || 'N/A' }}</span>
      </template>
      <template #col-url_publicacao="{ value }">
        <a
          v-if="value"
          :href="value"
          target="_blank"
          class="text-brand-blue hover:underline flex items-center gap-1"
        >
          <Icon name="lucide:external-link" class="w-3 h-3" />
          Ver Norma
        </a>
        <span v-else class="text-gray-400">-</span>
      </template>
    </BaseDataTable>

    <!-- Create/Edit Modal -->
    <BaseModal
      :show="showModal"
      :title="isEditing ? 'Editar Norma' : 'Nova Norma'"
      :confirm-label="isEditing ? 'Salvar Alterações' : 'Criar Norma'"
      :loading="submitting"
      @close="closeModal"
      @confirm="saveNorma"
    >
      <form class="space-y-4" @submit.prevent="saveNorma">
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
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Nome da Norma *</label>
          <input
            v-model="form.nome_norma"
            type="text"
            required
            placeholder="Ex: Portaria nº 123/2023"
            class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">Ementa *</label>
          <textarea
            v-model="form.ementa"
            required
            rows="3"
            placeholder="Breve descrição da norma..."
            class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all resize-none"
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">URL de Publicação</label>
          <input
            v-model="form.url_publicacao"
            type="url"
            placeholder="https://..."
            class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all"
          />
        </div>
      </form>
    </BaseModal>

    <!-- Delete Confirmation Modal -->
    <BaseModal
      :show="showDeleteModal"
      title="Excluir Norma"
      confirm-label="Excluir"
      :loading="submitting"
      @close="showDeleteModal = false"
      @confirm="deleteNorma"
    >
      <div class="flex flex-col items-center text-center py-4">
        <div class="w-16 h-16 bg-red-50 rounded-full flex items-center justify-center text-red-500 mb-4">
          <Icon name="lucide:alert-triangle" class="w-8 h-8" />
        </div>
        <p class="text-gray-700 dark:text-gray-300">
          Tem certeza que deseja excluir a norma <span class="font-bold text-gray-900 dark:text-white">{{ itemToDelete?.nome_norma }}</span>?
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
const normas = ref([])
const programas = ref([])
const showModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)
const itemToDelete = ref(null)

const columns = [
  { key: 'id_programa', label: 'Programa' },
  { key: 'nome_norma', label: 'Norma' },
  { key: 'ementa', label: 'Ementa', class: 'max-w-xs truncate' },
  { key: 'url_publicacao', label: 'Link' },
]

const form = reactive({
  id: '',
  id_programa: '',
  nome_norma: '',
  ementa: '',
  url_publicacao: ''
})

const fetchNormas = async () => {
  loading.value = true
  try {
    normas.value = await api('/api/normas/')
  } catch (error) {
    console.error('Erro ao buscar normas:', error)
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
  Object.assign(form, { id: '', id_programa: '', nome_norma: '', ementa: '', url_publicacao: '' })
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

const saveNorma = async () => {
  if (!form.id_programa || !form.nome_norma || !form.ementa) return
  
  submitting.value = true
  try {
    if (isEditing.value) {
      await api(`/api/normas/${form.id}`, {
        method: 'PATCH',
        body: {
          id_programa: form.id_programa,
          nome_norma: form.nome_norma,
          ementa: form.ementa,
          url_publicacao: form.url_publicacao
        }
      })
    } else {
      await api('/api/normas/', {
        method: 'POST',
        body: {
          id_programa: form.id_programa,
          nome_norma: form.nome_norma,
          ementa: form.ementa,
          url_publicacao: form.url_publicacao
        }
      })
    }
    await fetchNormas()
    closeModal()
  } catch (error) {
    console.error('Erro ao salvar norma:', error)
  } finally {
    submitting.value = false
  }
}

const confirmDelete = (item: any) => {
  itemToDelete.value = item
  showDeleteModal.value = true
}

const deleteNorma = async () => {
  if (!itemToDelete.value) return
  
  submitting.value = true
  try {
    await api(`/api/normas/${itemToDelete.value.id}`, {
      method: 'DELETE'
    })
    await fetchNormas()
    showDeleteModal.value = false
  } catch (error) {
    console.error('Erro ao excluir norma:', error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchNormas()
  fetchProgramas()
})
</script>
