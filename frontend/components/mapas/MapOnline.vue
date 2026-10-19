<template>
  <div class="relative h-full w-full bg-slate-50 dark:bg-slate-900 flex flex-col justify-center items-center">
    <!-- Indicador de Carregamento -->
    <div v-if="loading" class="flex flex-col items-center gap-3">
      <div class="w-10 h-10 border-4 border-[#1714EF] border-t-transparent rounded-full animate-spin"></div>
      <span class="text-sm font-semibold text-gray-500">Gerando mapa analítico no servidor...</span>
    </div>

    <!-- Mensagem de Erro -->
    <div v-else-if="error" class="flex flex-col items-center gap-3 max-w-sm text-center p-6 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900 rounded-2xl">
      <Icon name="lucide:alert-triangle" size="32" class="text-red-500" />
      <span class="text-sm font-bold text-red-700 dark:text-red-400">Falha ao obter mapa online</span>
      <p class="text-xs text-red-600 dark:text-red-300">{{ error }}</p>
      <BaseButton variant="ghost" size="sm" @click="loadMap" class="mt-2">Tentar Novamente</BaseButton>
    </div>

    <!-- Iframe com mapa Folium -->
    <iframe
      v-else-if="iframeUrl"
      :src="iframeUrl"
      class="w-full h-full border-none rounded-2xl shadow-sm"
      allow="geolocation"
    ></iframe>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useApi } from '~/composables/useApi'

const props = defineProps<{
  filters: {
    programa?: string
    ano?: string
    trimestre?: string
    municipio?: string
    status?: string
    data_inicio?: string
    data_fim?: string
  }
}>()

const iframeUrl = ref<string | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const api = useApi()

const loadMap = async () => {
  loading.value = true
  error.value = null
  iframeUrl.value = null

  try {
    // Transforma filtros reativos em query params
    const queryParams = new URLSearchParams()
    
    if (props.filters.programa) queryParams.append('id_programa', props.filters.programa)
    if (props.filters.ano) queryParams.append('ano', props.filters.ano)
    if (props.filters.trimestre) queryParams.append('trimestre', props.filters.trimestre)
    if (props.filters.municipio) queryParams.append('municipio', props.filters.municipio)
    if (props.filters.status) queryParams.append('status', props.filters.status)
    if (props.filters.data_inicio) queryParams.append('data_inicio', props.filters.data_inicio)
    if (props.filters.data_fim) queryParams.append('data_fim', props.filters.data_fim)

    const response = await api<{ url: string; total_markers: number }>('/api/relatorio-mapa/visualizar?' + queryParams.toString())

    if (response && response.url) {
      // Mitigação contra conflitos de Hosts de Docker/localhost
      // Extrai o path relativo '/mapas_temp/mapa_xxx.html' e concatena com o endereço de rede cliente da API
      const urlStr = response.url
      const index = urlStr.indexOf('/mapas_temp')
      if (index !== -1) {
        const relativePath = urlStr.substring(index)
        const config = useRuntimeConfig()
        iframeUrl.value = (config.public.apiBase || 'http://localhost:8000') + relativePath
      } else {
        iframeUrl.value = urlStr
      }
    } else {
      error.value = 'O servidor não retornou uma URL válida para o mapa.'
    }
  } catch (err: any) {
    console.error('[MapOnline] Erro ao carregar mapa:', err)
    error.value = err.data?.detail || 'Não foi possível conectar à API de mapas geográficos.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadMap()
})

// Recarrega o mapa sempre que os filtros mudarem
watch(() => props.filters, () => {
  loadMap()
}, { deep: true })
</script>
