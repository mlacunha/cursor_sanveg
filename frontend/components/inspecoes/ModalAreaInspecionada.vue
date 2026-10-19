<template>
  <BaseModal :title="isEdit ? 'Editar Área Inspecionada' : 'Adicionar Área Inspecionada'" @close="$emit('close')">
    <form @submit.prevent="submitForm" class="space-y-5">
      <!-- Nome do Local / Talhão -->
      <div>
        <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
          Identificação do Local (Talhão/Bloco) <span class="text-red-500">*</span>
        </label>
        <input
          v-model="form.nome_local"
          type="text"
          required
          placeholder="Ex: Talhão 4A - Citros"
          class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
        />
      </div>

      <!-- Tipo de Área -->
      <div>
        <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
          Tipo de Área <span class="text-red-500">*</span>
        </label>
        <select
          v-model="form.tipo_area"
          required
          class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
        >
          <option value="" disabled>Selecione...</option>
          <option value="pomar_comercial">Pomar Comercial</option>
          <option value="viveiro">Viveiro / Estufa</option>
          <option value="plantiu_domestico">Plantio Doméstico</option>
          <option value="area_silvestre">Área Silvestre / Mata</option>
          <option value="outro">Outro</option>
        </select>
      </div>

      <!-- Coordenadas Geográficas -->
      <div class="grid grid-cols-2 gap-4 bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl border border-slate-100 dark:border-slate-800/80">
        <div class="col-span-2 flex items-center justify-between">
          <span class="text-xs font-bold text-slate-500 uppercase tracking-wider">Coordenadas GPS (WGS84)</span>
          <button
            type="button"
            @click="captureGPS"
            :disabled="capturingGPS"
            class="flex items-center gap-1.5 text-xs font-bold text-blue-600 bg-blue-50 hover:bg-blue-100 border border-blue-100 px-3 py-1.5 rounded-lg active:scale-95 transition-all disabled:opacity-50"
          >
            <Icon :name="capturingGPS ? 'lucide:loader-2' : 'lucide:map-pin'" :class="{ 'animate-spin': capturingGPS }" size="12" />
            <span>{{ capturingGPS ? 'Obtendo...' : 'Obter Localização' }}</span>
          </button>
        </div>

        <div>
          <label class="block text-xs font-semibold text-gray-500 mb-1">Latitude</label>
          <input
            v-model="form.latitude"
            type="text"
            placeholder="Ex: -3.8541"
            class="w-full px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm outline-none"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-gray-500 mb-1">Longitude</label>
          <input
            v-model="form.longitude"
            type="text"
            placeholder="Ex: -52.5012"
            class="w-full px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm outline-none"
          />
        </div>

        <p v-if="gpsError" class="col-span-2 text-[10px] text-red-500 flex items-center gap-1">
          <Icon name="lucide:alert-circle" size="10" />
          <span>{{ gpsError }}</span>
        </p>
      </div>

      <!-- Observações -->
      <div>
        <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
          Observações (Opcional)
        </label>
        <textarea
          v-model="form.obs"
          rows="2"
          placeholder="Alguma particularidade desta área..."
          class="w-full px-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all resize-none"
        ></textarea>
      </div>

      <div class="flex justify-end gap-3 pt-2">
        <BaseButton variant="ghost" type="button" @click="$emit('close')">
          Cancelar
        </BaseButton>
        <BaseButton variant="primary" type="submit">
          Confirmar Área
        </BaseButton>
      </div>
    </form>
  </BaseModal>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { gerarIdLocal } from '~/utils/db'

const props = defineProps<{
  initialData?: any
  isEdit?: boolean
}>()

const emit = defineEmits(['close', 'submit'])

const form = ref({
  id: '',
  nome_local: '',
  tipo_area: '',
  latitude: '',
  longitude: '',
  obs: '',
  programas: [] as any[]
})

const capturingGPS = ref(false)
const gpsError = ref<string | null>(null)

onMounted(() => {
  if (props.initialData) {
    form.value = {
      ...form.value,
      ...props.initialData
    }
  } else {
    form.value.id = gerarIdLocal()
  }
})

const captureGPS = () => {
  if (!navigator.geolocation) {
    gpsError.value = 'Geolocalização não suportada neste navegador.'
    return
  }

  capturingGPS.value = true
  gpsError.value = null

  navigator.geolocation.getCurrentPosition(
    (position) => {
      form.value.latitude = String(position.coords.latitude)
      form.value.longitude = String(position.coords.longitude)
      capturingGPS.value = false
    },
    (error) => {
      capturingGPS.value = false
      switch (error.code) {
        case error.PERMISSION_DENIED:
          gpsError.value = 'Permissão de GPS negada pelo usuário.'
          break
        case error.POSITION_UNAVAILABLE:
          gpsError.value = 'Sinal GPS indisponível no local.'
          break
        case error.TIMEOUT:
          gpsError.value = 'Tempo esgotado ao buscar localização.'
          break
        default:
          gpsError.value = 'Erro desconhecido ao obter GPS.'
      }
    },
    { timeout: 10000, enableHighAccuracy: true }
  )
}

const submitForm = () => {
  emit('submit', { ...form.value })
}
</script>
