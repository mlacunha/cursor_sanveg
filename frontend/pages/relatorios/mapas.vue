<template>
  <div class="space-y-6">
    <!-- Header com Chaveador de Modo -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 dark:text-white">Mapa de Levantamentos</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Histórico e focos de ocorrência fitossanitária georreferenciados
        </p>
      </div>

      <!-- Controles de Conectividade do Mapa -->
      <div class="flex items-center gap-3 bg-slate-50 dark:bg-slate-950 p-2 rounded-xl border border-slate-100 dark:border-slate-800">
        <!-- Indicador de Rede -->
        <span
          class="flex items-center gap-1 text-[10px] font-black px-2.5 py-1 rounded-lg border uppercase tracking-wider shadow-sm"
          :class="isOnline ? 'text-emerald-600 bg-emerald-50 border-emerald-100' : 'text-slate-500 bg-slate-100 border-slate-200'"
        >
          <Icon :name="isOnline ? 'lucide:wifi' : 'lucide:wifi-off'" size="10" />
          <span>{{ isOnline ? 'Online' : 'Offline' }}</span>
        </span>

        <div class="w-px h-5 bg-slate-200 dark:bg-slate-800"></div>

        <!-- Chaveador Manual -->
        <button
          @click="forceOffline = !forceOffline"
          class="flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-lg active:scale-95 transition-all"
          :class="[
            forceOffline
              ? 'bg-amber-100 text-amber-700 border border-amber-200'
              : 'bg-white dark:bg-slate-900 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:bg-gray-50'
          ]"
        >
          <Icon name="lucide:plane" size="12" />
          <span>{{ forceOffline ? 'Forçando Offline' : 'Forçar Offline' }}</span>
        </button>
      </div>
    </div>

    <!-- Barra de Filtros (Apenas aplicável/exibida com clareza no modo Online) -->
    <div class="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm space-y-4">
      <div class="flex items-center justify-between border-b border-slate-50 dark:border-slate-800 pb-2">
        <span class="text-xs font-bold text-gray-400 uppercase tracking-widest">Filtros de Mapa Analítico</span>
        <button @click="clearFilters" class="text-xs text-blue-600 font-bold hover:underline">Limpar Filtros</button>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <!-- Programa -->
        <div>
          <label class="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">Programa</label>
          <select
            v-model="filters.programa"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-xs outline-none"
          >
            <option value="">Todos</option>
            <option v-for="p in programas" :key="p.id" :value="p.id">{{ p.nome }}</option>
          </select>
        </div>

        <!-- Município -->
        <div>
          <label class="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">Município</label>
          <select
            v-model="filters.municipio"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-xs outline-none"
          >
            <option value="">Todos</option>
            <option v-for="m in municipios" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>

        <!-- Ano -->
        <div>
          <label class="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">Ano</label>
          <select
            v-model="filters.ano"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-xs outline-none"
          >
            <option value="">Todos</option>
            <option v-for="y in anos" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>

        <!-- Trimestre -->
        <div>
          <label class="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">Trimestre</label>
          <select
            v-model="filters.trimestre"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-xs outline-none"
          >
            <option value="">Todos</option>
            <option value="1">1º Trimestre</option>
            <option value="2">2º Trimestre</option>
            <option value="3">3º Trimestre</option>
            <option value="4">4º Trimestre</option>
          </select>
        </div>

        <!-- Status -->
        <div>
          <label class="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">Status</label>
          <select
            v-model="filters.status"
            class="w-full px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-xs outline-none"
          >
            <option value="">Todos</option>
            <option value="NORMAL">Normal (Azul)</option>
            <option value="SUSPEITA">Suspeita (Laranja)</option>
            <option value="POSITIVO">Positivo / Foco (Vermelho)</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Área de Exibição do Mapa (Híbrido) -->
    <div class="h-[600px] w-full bg-white dark:bg-slate-900 rounded-2xl overflow-hidden border border-gray-100 dark:border-gray-800 shadow-sm">
      <MapOnline
        v-if="currentMode === 'online'"
        :filters="filters"
      />
      <MapOffline
        v-else
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { db } from '~/utils/db'
import { useSync } from '~/composables/useSync'
import MapOffline from '~/components/mapas/MapOffline.vue'
import MapOnline from '~/components/mapas/MapOnline.vue'

definePageMeta({
  layout: 'default'
})

const { isOnline } = useSync()
const forceOffline = ref(false)

const currentMode = computed(() => {
  return (isOnline.value && !forceOffline.value) ? 'online' : 'offline'
})

// Estado de Filtros
const filters = ref({
  programa: '',
  ano: '',
  trimestre: '',
  municipio: '',
  status: '',
  data_inicio: '',
  data_fim: ''
})

// Opções dinâmicas dos seletores
const programas = ref<any[]>([])
const municipios = ref<string[]>([])
const anos = ref<string[]>([])

const loadFilters = async () => {
  if (process.client && db) {
    try {
      const [progs, props, termos] = await Promise.all([
        db.programas.toArray(),
        db.propriedades.toArray(),
        db.termo_inspecao.toArray()
      ])

      programas.value = progs
      municipios.value = [...new Set(props.map(p => p.municipio).filter(Boolean))].sort() as string[]
      
      const years = new Set<string>()
      termos.forEach(t => {
        const dateVal = t.data_inspecao || (t.data as string)
        if (dateVal && dateVal.length >= 4) {
          years.add(dateVal.substring(0, 4))
        }
      })
      
      // Fallback years if empty
      if (years.size === 0) {
        years.add('2024')
        years.add('2025')
        years.add('2026')
      }
      anos.value = [...years].sort((a, b) => Number(b) - Number(a))

    } catch (err) {
      console.error('[Mapas] Erro ao carregar filtros locais:', err)
    }
  }
}

onMounted(() => {
  loadFilters()
})

const clearFilters = () => {
  filters.value = {
    programa: '',
    ano: '',
    trimestre: '',
    municipio: '',
    status: '',
    data_inicio: '',
    data_fim: ''
  }
}
</script>
