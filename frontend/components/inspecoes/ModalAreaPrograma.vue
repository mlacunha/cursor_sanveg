<template>
  <BaseModal :title="isEdit ? 'Editar Monitoramento de Praga' : 'Adicionar Monitoramento de Praga'" @close="$emit('close')">
    <form @submit.prevent="submitForm" class="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Programa de Monitoramento -->
        <div class="md:col-span-2">
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
            Programa Fitossanitário <span class="text-red-500">*</span>
          </label>
          <select
            v-model="form.id_programa"
            required
            :disabled="isEdit"
            class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all disabled:opacity-60"
          >
            <option value="" disabled>Selecione...</option>
            <option
              v-for="prog in programas"
              :key="prog.id"
              :value="prog.id"
            >
              {{ prog.nome }}
            </option>
          </select>
        </div>

        <!-- Cultura / Especie -->
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Espécie (Cultura)</label>
          <input
            v-model="form.especie"
            type="text"
            placeholder="Ex: Citrus sinensis (L.) Osbeck"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm outline-none"
          />
        </div>

        <!-- Variedade -->
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Variedade</label>
          <input
            v-model="form.variedade"
            type="text"
            placeholder="Ex: Laranja Pêra"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm outline-none"
          />
        </div>

        <!-- Material Multiplicação -->
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Material de Multiplicação</label>
          <input
            v-model="form.material_multiplicacao"
            type="text"
            placeholder="Ex: Muda enxertada"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm outline-none"
          />
        </div>

        <!-- Origem -->
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Origem do Material</label>
          <input
            v-model="form.origem"
            type="text"
            placeholder="Ex: Viveiro Credenciado"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm outline-none"
          />
        </div>

        <div class="md:col-span-2 border-t border-gray-100 dark:border-gray-800 pt-3 mt-1">
          <span class="text-xs font-bold text-gray-400 uppercase tracking-wider">Estatísticas do Plantio</span>
        </div>

        <!-- Idade do Plantio -->
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Idade do Plantio (Anos)</label>
          <input
            v-model.number="form.idade_plantio"
            type="number"
            step="0.1"
            placeholder="0.0"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm outline-none"
          />
        </div>

        <!-- Área Plantada (ha) -->
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Área Plantada (Hectares)</label>
          <input
            v-model.number="form.area_plantada"
            type="number"
            step="0.01"
            placeholder="0.00"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm outline-none"
          />
        </div>

        <!-- Número de Plantas Existentes -->
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Nº Total de Plantas</label>
          <input
            v-model.number="form.numero_plantas"
            type="number"
            placeholder="0"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm outline-none"
          />
        </div>

        <!-- Número de Plantas Inspecionadas -->
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Nº Plantas Inspecionadas <span class="text-red-500">*</span></label>
          <input
            v-model.number="form.numero_inspecionadas"
            type="number"
            required
            placeholder="0"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm outline-none"
          />
        </div>

        <!-- Número de Plantas Suspeitas -->
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Nº Plantas Suspeitas <span class="text-red-500">*</span></label>
          <input
            v-model.number="form.numero_suspeitas"
            type="number"
            required
            placeholder="0"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm outline-none"
          />
        </div>

        <!-- Resultado Avaliação -->
        <div>
          <label class="block text-xs font-semibold text-gray-600 mb-1">Avaliação / Resultado <span class="text-red-500">*</span></label>
          <select
            v-model="form.resultado"
            required
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm outline-none"
          >
            <option value="NORMAL">NORMAL</option>
            <option value="SUSPEITA">SUSPEITA</option>
            <option value="POSITIVO">POSITIVO / FOCO</option>
          </select>
        </div>

        <!-- Observações -->
        <div class="md:col-span-2">
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
            Notas da Avaliação
          </label>
          <textarea
            v-model="form.obs"
            rows="2"
            placeholder="Sintomas observados ou anotações..."
            class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all resize-none"
          ></textarea>
        </div>
      </div>

      <div class="flex justify-end gap-3 pt-2">
        <BaseButton variant="ghost" type="button" @click="$emit('close')">
          Cancelar
        </BaseButton>
        <BaseButton variant="primary" type="submit">
          Salvar Avaliação
        </BaseButton>
      </div>
    </form>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { db, type Programa, gerarIdLocal } from '~/utils/db'

const props = defineProps<{
  initialData?: any
  isEdit?: boolean
}>()

const emit = defineEmits(['close', 'submit'])

const form = ref({
  id: '',
  id_programa: '',
  especie: '',
  variedade: '',
  material_multiplicacao: '',
  origem: '',
  idade_plantio: undefined as number | undefined,
  area_plantada: undefined as number | undefined,
  numero_plantas: undefined as number | undefined,
  numero_inspecionadas: 0,
  numero_suspeitas: 0,
  resultado: 'NORMAL',
  obs: '',
  amostras: [] as any[]
})

const programas = ref<Programa[]>([])

const loadProgramas = async () => {
  if (process.client && db) {
    try {
      programas.value = await db.programas.toArray()
    } catch (err) {
      console.error('[ModalAreaPrograma] Erro ao carregar programas:', err)
    }
  }
}

onMounted(() => {
  loadProgramas()
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
