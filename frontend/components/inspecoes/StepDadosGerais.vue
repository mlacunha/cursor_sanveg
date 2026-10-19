<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-lg font-bold text-gray-800 dark:text-white">1. Informações Gerais</h2>
      <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Defina a propriedade e os fiscais envolvidos na inspeção</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Seleção de Propriedade Rural (Obrigatório) -->
      <div class="md:col-span-2">
        <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
          Propriedade Rural <span class="text-red-500">*</span>
        </label>
        <select
          :value="idPropriedade"
          @change="$emit('update:idPropriedade', ($event.target as HTMLSelectElement).value)"
          required
          class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
        >
          <option value="" disabled>Selecione a propriedade inspecionada...</option>
          <option
            v-for="prop in propriedades"
            :key="prop.id"
            :value="prop.id"
          >
            {{ prop.nome }} - {{ prop.municipio }}
          </option>
        </select>
        <p v-if="propriedades.length === 0" class="text-xs text-amber-500 mt-1 flex items-center gap-1">
          <Icon name="lucide:alert-triangle" size="12" />
          <span>Nenhuma propriedade cadastrada localmente. Cadastre-a antes de iniciar.</span>
        </p>
      </div>

      <!-- Data da Inspeção (Obrigatório) -->
      <div>
        <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
          Data da Inspeção <span class="text-red-500">*</span>
        </label>
        <input
          :value="dataInspecao"
          @input="$emit('update:dataInspecao', ($event.target as HTMLInputElement).value)"
          type="date"
          required
          class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
        />
      </div>

      <!-- Fiscal Auxiliar (Opcional) -->
      <div>
        <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
          Fiscal Auxiliar (Opcional)
        </label>
        <select
          :value="idAuxiliar"
          @change="$emit('update:idAuxiliar', ($event.target as HTMLSelectElement).value)"
          class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
        >
          <option value="">Nenhum fiscal auxiliar</option>
          <option
            v-for="user in fiscais"
            :key="user.id"
            :value="user.id"
          >
            {{ user.nome }}
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { db, type Propriedade, type Usuario } from '~/utils/db'

defineProps<{
  idPropriedade: string
  dataInspecao: string
  idAuxiliar: string
}>()

defineEmits(['update:idPropriedade', 'update:dataInspecao', 'update:idAuxiliar'])

const propriedades = ref<Propriedade[]>([])
const fiscais = ref<Usuario[]>([])

const loadOptions = async () => {
  if (process.client && db) {
    try {
      const [props, users] = await Promise.all([
        db.propriedades.toArray(),
        db.usuarios.toArray()
      ])
      propriedades.value = props.sort((a, b) => (a.nome || '').localeCompare(b.nome || ''))
      fiscais.value = users.sort((a, b) => (a.nome || '').localeCompare(b.nome || ''))
    } catch (err) {
      console.error('[StepDadosGerais] Erro ao carregar dados locais:', err)
    }
  }
}

onMounted(() => {
  loadOptions()
})
</script>
