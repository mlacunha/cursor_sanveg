<template>
  <div class="space-y-6">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 dark:text-white">Termos de Inspeção</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Gerencie os termos de inspeções fitossanitárias executadas em campo</p>
      </div>
      <BaseButton
        variant="primary"
        icon="lucide:plus"
        @click="navigateToAdd"
      >
        Nova Inspeção
      </BaseButton>
    </div>

    <!-- Tabela Principal -->
    <BaseDataTable
      title="Inspeções Registradas"
      subtitle="Inspeções salvas localmente prontas para sincronização"
      :columns="columns"
      :items="tableItems"
      :loading="loading"
      search-placeholder="Buscar inspeção por número ou propriedade..."
      show-row-actions
      @edit="navigateToEdit"
      @delete="confirmDelete"
    >
      <!-- Customização de colunas -->
      <template #col-numero="{ item }">
        <span class="font-bold text-gray-800 dark:text-white">
          {{ item.numero_ti || item.termo_inspecao || item.id.substring(0, 8) }}
        </span>
      </template>

      <template #col-propriedade="{ item }">
        <span>{{ getPropriedadeName(item.id_propriedade) }}</span>
      </template>

      <template #col-data_inspecao="{ item }">
        <span>{{ formatDate(item.data_inspecao || item.data) }}</span>
      </template>

      <template #col-usuario="{ item }">
        <span class="text-xs text-gray-500">{{ getUserName(item.id_usuario) }}</span>
      </template>

      <template #col-status="{ item }">
        <span
          class="px-2.5 py-1 rounded-md text-[10px] font-black uppercase tracking-widest shadow-sm"
          :class="getInspectionStatusClass(item.id)"
        >
          {{ getInspectionStatusLabel(item.id) }}
        </span>
      </template>
    </BaseDataTable>

    <!-- Modal de Confirmação de Exclusão -->
    <BaseModal
      v-if="showDeleteModal"
      title="Confirmar Exclusão de Inspeção"
      @close="showDeleteModal = false"
    >
      <div class="space-y-4">
        <p class="text-sm text-gray-600 dark:text-gray-300">
          Tem certeza que deseja excluir o Termo de Inspeção número
          <span class="font-bold text-gray-850 dark:text-white">
            {{ selectedItem?.numero_ti || selectedItem?.termo_inspecao || selectedItem?.id.substring(0, 8) }}
          </span>?
        </p>
        <p class="text-xs text-red-600 bg-red-50 dark:bg-red-950/20 px-3 py-2 rounded-lg border border-red-100 dark:border-red-900/50">
          Esta ação excluirá o termo e todas as áreas físicas, pragas e amostras vinculadas localmente. A exclusão será enviada ao servidor no próximo sincronismo.
        </p>
        
        <div class="flex justify-end gap-3 pt-2">
          <BaseButton variant="ghost" @click="showDeleteModal = false">
            Cancelar
          </BaseButton>
          <BaseButton variant="danger" @click="handleDelete">
            Confirmar Exclusão
          </BaseButton>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { db, offlineDelete } from '~/utils/db'

definePageMeta({
  layout: 'default'
})

interface TableItem {
  id: string
  id_propriedade: string
  id_usuario?: string
  data_inspecao?: string
  data?: string
  numero_ti?: string
  termo_inspecao?: string
}

const tableItems = ref<TableItem[]>([])
const propriedadesMap = ref<Map<string, string>>(new Map())
const usuariosMap = ref<Map<string, string>>(new Map())
const areaProgramasMap = ref<Map<string, any[]>>(new Map())
const areasMap = ref<Map<string, string[]>>(new Map())

const loading = ref(false)
const showDeleteModal = ref(false)
const selectedItem = ref<TableItem | null>(null)

// Configuração das colunas
const columns = [
  { key: 'numero', label: 'Número / Ficha' },
  { key: 'propriedade', label: 'Propriedade Rural' },
  { key: 'data_inspecao', label: 'Data da Inspeção' },
  { key: 'usuario', label: 'Fiscal' },
  { key: 'status', label: 'Resultado' }
]

// Carrega os dados do Dexie
const loadData = async () => {
  if (!process.client || !db) return
  
  loading.value = true
  try {
    // Busca dados no Dexie
    const [termos, props, users, areas, ap] = await Promise.all([
      db.termo_inspecao.toArray(),
      db.propriedades.toArray(),
      db.usuarios.toArray(),
      db.area_inspecionada.toArray(),
      db.area_programa.toArray()
    ])

    // Mapeia propriedades para acesso rápido
    const pMap = new Map<string, string>()
    props.forEach(p => pMap.set(p.id, p.nome || ''))
    propriedadesMap.value = pMap

    // Mapeia usuários para acesso rápido
    const uMap = new Map<string, string>()
    users.forEach(u => uMap.set(u.id, u.nome || ''))
    usuariosMap.value = uMap

    // Agrupa áreas físicas por termo de inspeção
    const aMap = new Map<string, string[]>()
    areas.forEach(a => {
      if (a.id_termo_inspecao) {
        const list = aMap.get(a.id_termo_inspecao) || []
        list.push(a.id)
        aMap.set(a.id_termo_inspecao, list)
      }
    })
    areasMap.value = aMap

    // Agrupa programas/inspeções por área
    const apMap = new Map<string, any[]>()
    ap.forEach(p => {
      if (p.id_area) {
        const list = apMap.get(p.id_area) || []
        list.push(p)
        apMap.set(p.id_area, list)
      }
    })
    areaProgramasMap.value = apMap

    tableItems.value = termos.map(t => ({
      id: t.id,
      id_propriedade: t.id_propriedade || '',
      id_usuario: t.id_usuario,
      data_inspecao: t.data_inspecao,
      data: t.data as string | undefined,
      numero_ti: t.numero_ti,
      termo_inspecao: t.termo_inspecao as string | undefined
    }))
  } catch (err) {
    console.error('[Inspecoes] Erro ao carregar dados locais:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

const getPropriedadeName = (id: string) => {
  return propriedadesMap.value.get(id) || 'Propriedade Não Vinculada'
}

const getUserName = (id?: string) => {
  if (!id) return '-'
  return usuariosMap.value.get(id) || id
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr
  return date.toLocaleDateString('pt-BR')
}

// Determina o status geral da inspeção baseada nas sub-tabelas
const getInspectionStatusLabel = (termoId: string) => {
  const areaIds = areasMap.value.get(termoId) || []
  let hasPositivo = false
  let hasSuspeita = false

  for (const aid of areaIds) {
    const programas = areaProgramasMap.value.get(aid) || []
    for (const prog of programas) {
      const res = String(prog.resultado).toUpperCase()
      if (res === 'POSITIVO' || res === 'FOCO') hasPositivo = true
      if (res === 'SUSPEITA') hasSuspeita = true
    }
  }

  if (hasPositivo) return 'Positivo'
  if (hasSuspeita) return 'Suspeita'
  return 'Normal'
}

const getInspectionStatusClass = (termoId: string) => {
  const label = getInspectionStatusLabel(termoId)
  if (label === 'Positivo') return 'bg-red-100 text-red-700'
  if (label === 'Suspeita') return 'bg-amber-100 text-amber-700'
  return 'bg-blue-100 text-blue-700'
}

// Navegação
const navigateToAdd = () => {
  navigateTo('/inspecoes/novo')
}

const navigateToEdit = (item: TableItem) => {
  navigateTo(`/inspecoes/${item.id}`)
}

const confirmDelete = (item: TableItem) => {
  selectedItem.value = item
  showDeleteModal.value = true
}

const handleDelete = async () => {
  if (selectedItem.value && process.client && db) {
    try {
      const termoId = selectedItem.value.id
      
      // Busca todas as áreas físicas relacionadas para deletar em cascata
      const areasRelacionadas = await db.area_inspecionada
        .where('id_termo_inspecao')
        .equals(termoId)
        .toArray()
      
      for (const area of areasRelacionadas) {
        // Busca programas relacionados a essa área
        const programasRelacionados = await db.area_programa
          .where('id_area')
          .equals(area.id)
          .toArray()
        
        for (const prog of programasRelacionados) {
          // Deleta amostras coletadas
          const amostrasRelacionadas = await db.amostra_coletada
            .where('id_area_programa')
            .equals(prog.id)
            .toArray()
          
          for (const am of amostrasRelacionadas) {
            await offlineDelete('amostra_coletada', am.id)
          }
          await offlineDelete('area_programa', prog.id)
        }
        await offlineDelete('area_inspecionada', area.id)
      }
      
      // Finalmente deleta o termo de inspeção
      await offlineDelete('termo_inspecao', termoId)
      
      showDeleteModal.value = false
      selectedItem.value = null
      await loadData()
    } catch (err) {
      console.error('[Inspecoes] Erro ao excluir termo localmente:', err)
    }
  }
}
</script>
