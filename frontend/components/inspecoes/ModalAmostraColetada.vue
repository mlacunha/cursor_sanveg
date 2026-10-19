<template>
  <BaseModal :title="isEdit ? 'Editar Amostra Coletada' : 'Adicionar Amostra Coletada'" @close="$emit('close')">
    <form @submit.prevent="submitForm" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Número do Envelope / Código Coleta -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
            Número do Envelope <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.envelope"
            type="text"
            required
            placeholder="Ex: ENV-12345"
            class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
          />
        </div>

        <!-- Parte Coletada -->
        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
            Parte da Planta Coletada <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.parte_coletada"
            type="text"
            required
            placeholder="Ex: Folha com sintomas, Ramos"
            class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
          />
        </div>

        <!-- Laboratório Destinatário -->
        <div class="md:col-span-2">
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
            Laboratório Destinatário <span class="text-red-500">*</span>
          </label>
          <select
            v-model="form.id_laboratorio"
            required
            class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
          >
            <option value="" disabled>Selecione o laboratório...</option>
            <option
              v-for="lab in laboratorios"
              :key="lab.id"
              :value="lab.id"
            >
              {{ lab.nome }}
            </option>
          </select>
          <p v-if="laboratorios.length === 0" class="text-xs text-amber-500 mt-1 flex items-center gap-1">
            <Icon name="lucide:alert-triangle" size="12" />
            <span>Nenhum laboratório cadastrado localmente. Sincronize antes de selecionar.</span>
          </p>
        </div>

        <!-- Data do Envio -->
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Data de Envio</label>
          <input
            v-model="form.data_envio_laboratorio"
            type="date"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm outline-none"
          />
        </div>

        <!-- Processo SEI -->
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Nº Processo SEI (Opcional)</label>
          <input
            v-model="form.processo_sei"
            type="text"
            placeholder="Ex: 001.0002/2026"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm outline-none"
          />
        </div>
      </div>

      <div class="flex justify-end gap-3 pt-2">
        <BaseButton variant="ghost" type="button" @click="$emit('close')">
          Cancelar
        </BaseButton>
        <BaseButton variant="primary" type="submit">
          Confirmar Amostra
        </BaseButton>
      </div>
    </form>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { db, type Laboratorio, gerarIdLocal } from '~/utils/db'

const props = defineProps<{
  initialData?: any
  isEdit?: boolean
}>()

const emit = defineEmits(['close', 'submit'])

const form = ref({
  id: '',
  envelope: '',
  parte_coletada: '',
  data_envio_laboratorio: new Date().toISOString().split('T')[0],
  id_laboratorio: '',
  processo_sei: ''
})

const laboratorios = ref<Laboratorio[]>([])

const loadLaboratorios = async () => {
  if (process.client && db) {
    try {
      laboratorios.value = await db.laboratorios.toArray()
    } catch (err) {
      console.error('[ModalAmostraColetada] Erro ao carregar laboratórios:', err)
    }
  }
}

onMounted(() => {
  loadLaboratorios()
  if (props.initialData) {
    form.value = {
      ...form.value,
      ...props.initialData
    }
  } else {
    form.value.id = gerarIdLocal()
  }
})

const submitForm = () => {
  emit('submit', { ...form.value })
}
</script>
