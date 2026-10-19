<template>
  <div class="flex flex-col gap-1.5 w-full md:w-auto">
    <!-- Erros de Sincronismo -->
    <div
      v-if="syncErrors.length > 0"
      class="flex items-start gap-2 bg-red-50 border border-red-200 text-red-700 text-xs px-3 py-2 rounded-xl shadow-sm transition-all duration-300"
    >
      <Icon name="lucide:alert-circle" size="14" class="mt-0.5 shrink-0" />
      <div class="flex-1">
        <span class="font-bold">{{ syncErrors.length }} registro(s) não sincronizados:</span>
        <ul class="mt-0.5 list-disc list-inside space-y-0.5">
          <li v-for="(error, index) in syncErrors" :key="index">{{ error }}</li>
        </ul>
      </div>
      <button
        @click="clearErrors"
        class="text-red-400 hover:text-red-600 font-bold ml-1 transition-colors"
      >
        ×
      </button>
    </div>

    <!-- Barra Principal do SyncManager -->
    <div
      class="flex items-center justify-between md:justify-start gap-4 bg-white px-4 py-2.5 rounded-xl shadow-sm border border-slate-100 w-full"
    >
      <!-- Indicador Físico de Rede -->
      <div class="flex items-center shrink-0">
        <span
          v-if="isOnline"
          class="flex items-center gap-1.5 text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-100"
        >
          <Icon name="lucide:wifi" size="14" />
          <span class="hidden sm:inline">ONLINE</span>
        </span>
        <span
          v-else
          class="flex items-center gap-1.5 text-xs font-bold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200"
        >
          <Icon name="lucide:wifi-off" size="14" />
          <span class="hidden sm:inline">OFFLINE</span>
        </span>
      </div>

      <div class="h-6 w-px bg-slate-200 shrink-0"></div>

      <!-- Ações de Sincronismo -->
      <div class="flex items-center gap-3">
        <button
          @click="handleSync"
          :disabled="!isOnline || isSyncing"
          class="flex items-center gap-1.5 text-xs font-bold px-3.5 py-2 rounded-lg transition-all duration-200"
          :class="[
            isSyncing || !isOnline
              ? 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-150'
              : 'bg-blue-50 text-blue-600 hover:bg-blue-100 border border-blue-100 active:scale-95'
          ]"
        >
          <Icon
            name="lucide:refresh-cw"
            size="14"
            :class="{ 'animate-spin': isSyncing }"
          />
          <span>{{ isSyncing ? 'Sincronizando...' : 'Sincronizar Agora' }}</span>
        </button>

        <!-- Última Sincronização -->
        <div class="hidden md:flex flex-col">
          <span class="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Última Sincronização</span>
          <span class="text-xs text-slate-700 font-medium flex items-center gap-1 mt-0.5">
            <template v-if="lastSync">
              <Icon name="lucide:check-circle" size="11" class="text-emerald-500" />
              <span>{{ lastSync }}</span>
            </template>
            <template v-else>
              <span class="text-slate-400 italic">Aguardando...</span>
            </template>
          </span>
        </div>
      </div>

      <div class="h-6 w-px bg-slate-200 shrink-0"></div>

      <!-- Contador de Fila Offline -->
      <div class="flex flex-col items-center justify-center px-2">
        <span class="hidden md:block text-[9px] text-slate-400 font-bold uppercase tracking-wider">Fila Offline</span>
        <span
          class="text-xs font-bold px-2 py-0.5 rounded-md mt-0.5"
          :class="[
            syncQueueLength > 0
              ? 'text-amber-600 bg-amber-50 border border-amber-100'
              : 'text-emerald-600 bg-emerald-50 border border-emerald-100'
          ]"
        >
          {{ syncQueueLength }} {{ syncQueueLength === 1 ? 'Registro' : 'Registros' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useSync } from '~/composables/useSync'

const {
  isOnline,
  isSyncing,
  lastSync,
  syncQueueLength,
  syncErrors,
  handleSync,
  initListeners
} = useSync()

// Inicializa e limpa listeners reativos de rede e timers
let cleanup: (() => void) | undefined

onMounted(() => {
  cleanup = initListeners()
})

onUnmounted(() => {
  if (cleanup) cleanup()
})

// Função local para limpar exibição de erros
const clearErrors = () => {
  syncErrors.value = []
}
</script>

<style scoped>
/* Transição suave de erro */
.transition-all {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>
