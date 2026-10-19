import { ref, onMounted, onUnmounted } from 'vue'
import { db } from '~/utils/db'
import { useAuthStore } from '~/stores/auth'
import { useApi } from '~/composables/useApi'

// Estados reativos compartilhados (Singleton no nível do composable para manter sincronia em toda a app)
const isOnline = ref(true)
const isSyncing = ref(false)
const lastSync = ref<string | null>(null)
const syncQueueLength = ref(0)
const syncErrors = ref<string[]>([])

export const useSync = () => {
  const authStore = useAuthStore()
  const api = useApi()

  // Atualiza o contador da fila local
  const refreshQueueLength = async () => {
    if (process.client && db) {
      try {
        syncQueueLength.value = await db.syncQueue.count()
      } catch (e) {
        console.error('[Sync] Erro ao contar fila offline:', e)
      }
    }
  }

  // Protocolo Bi-direcional de Sincronismo
  const handleSync = async () => {
    if (!process.client || !db) return
    if (!isOnline.value || isSyncing.value) return

    // Só sincroniza se estiver autenticado
    if (!authStore.token) {
      console.warn('[Sync] Sincronização ignorada: usuário não autenticado.')
      return
    }

    isSyncing.value = true
    syncErrors.value = []

    try {
      // ----------------------------------------------------
      // 1. FASE DE PUSH — Envia alterações locais para a API
      // ----------------------------------------------------
      const queueItems = await db.syncQueue.toArray()

      if (queueItems.length > 0) {
        console.log(`[Sync] Iniciando Push de ${queueItems.length} registros...`)
        
        const pushResponse = await api<{ processed_ids?: number[]; errors?: Array<{ error: string }> }>('/api/sync/push', {
          method: 'POST',
          body: { queue: queueItems }
        })

        // Se o servidor processou com sucesso, limpa os IDs locais correspondentes
        if (pushResponse?.processed_ids && pushResponse.processed_ids.length > 0) {
          await db.syncQueue.bulkDelete(pushResponse.processed_ids)
          console.log(`[Sync] Push concluído. ${pushResponse.processed_ids.length} registros sincronizados.`)
        }

        // Se houver erros parciais de push, exibe-os na tela
        if (pushResponse?.errors && pushResponse.errors.length > 0) {
          syncErrors.value = pushResponse.errors.map(e => e.error)
          console.error('[Sync] Erros durante o Push:', pushResponse.errors)
        }
      }

      // ----------------------------------------------------
      // 2. FASE DE PULL — Busca novos dados consolidados
      // ----------------------------------------------------
      console.log('[Sync] Iniciando Pull de tabelas consolidadas...')
      
      const pullResponse = await api<Record<string, any[]>>('/api/sync/pull', {
        method: 'GET'
      })

      if (pullResponse) {
        // Coleção de tabelas mapeadas
        const tables = [
          'programas', 'propriedades', 'produtores', 'termo_inspecao',
          'area_inspecionada', 'area_programa', 'amostra_coletada',
          'hospedeiros', 'normas', 'tipos_orgao', 'orgaos', 'unidades',
          'cargos', 'formacoes', 'laboratorios', 'usuarios'
        ]

        // Executa escritas bulkPut velozes e paralelas para cada tabela local
        const savePromises = tables.map(async (tableKey) => {
          const list = pullResponse[tableKey]
          if (list && list.length > 0) {
            const table = (db as any)[tableKey]
            if (table) {
              await table.bulkPut(list)
            }
          }
        })

        await Promise.all(savePromises)
        console.log('[Sync] Pull concluído com sucesso!')
      }

      // Atualiza data e hora do último sincronismo bem-sucedido
      const now = new Date().toLocaleTimeString()
      lastSync.value = now
      localStorage.setItem('lastSync', now)
      syncErrors.value = []

    } catch (error: any) {
      console.error('[Sync] Falha crítica de sincronização:', error)
      
      // Se retornar erro 401 (autorização expirada/inválida), força logout
      if (error?.response?.status === 401) {
        console.warn('[Sync] Token inválido ou expirado (401). Forçando logout.')
        authStore.logout()
        return
      }

      syncErrors.value.push('Falha na conexão ou erro interno do servidor ao sincronizar.')
    } finally {
      isSyncing.value = false
      await refreshQueueLength()
    }
  }

  // Gerenciadores de eventos do ciclo de vida no cliente
  let statusInterval: any = null
  let autoSyncInterval: any = null

  const initListeners = () => {
    if (!process.client) return

    // Carrega último sincronismo persistido
    const savedLastSync = localStorage.getItem('lastSync')
    if (savedLastSync) {
      lastSync.value = savedLastSync
    }

    // Monitora status físico da rede
    isOnline.value = navigator.onLine
    
    const setOnline = () => {
      isOnline.value = true
      // Tenta sincronizar automaticamente ao reestabelecer conexão
      handleSync()
    }
    const setOffline = () => {
      isOnline.value = false
    }

    window.addEventListener('online', setOnline)
    window.addEventListener('offline', setOffline)

    // Polling ultraleve para contar o tamanho da fila offline a cada 2s
    refreshQueueLength()
    statusInterval = setInterval(refreshQueueLength, 2000)

    // Temporizador de auto-sync (a cada 30s se online)
    autoSyncInterval = setInterval(() => {
      if (isOnline.value && authStore.token) {
        handleSync()
      }
    }, 30000)

    // Limpeza ao desmontar
    return () => {
      window.removeEventListener('online', setOnline)
      window.removeEventListener('offline', setOffline)
      if (statusInterval) clearInterval(statusInterval)
      if (autoSyncInterval) clearInterval(autoSyncInterval)
    }
  }

  return {
    isOnline,
    isSyncing,
    lastSync,
    syncQueueLength,
    syncErrors,
    handleSync,
    refreshQueueLength,
    initListeners
  }
}
