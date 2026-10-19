<template>
  <div class="max-w-6xl mx-auto space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between bg-white dark:bg-slate-900 p-6 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 dark:text-white">
          {{ isEditMode ? 'Editar Termo de Inspeção' : 'Novo Termo de Inspeção' }}
        </h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {{ isEditMode ? 'Atualize os dados e talhões da inspeção' : 'Cadastre as informações gerais, talhões vistoriados e colete amostras se necessário' }}
        </p>
      </div>
      <BaseButton variant="ghost" icon="lucide:arrow-left" @click="goBack">
        Voltar
      </BaseButton>
    </div>

    <!-- Navegação de Abas do Wizard -->
    <div class="flex border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-slate-900 p-2 rounded-xl shadow-sm gap-2">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="flex-1 py-3 px-4 rounded-lg font-bold text-sm transition-all duration-200 flex items-center justify-center gap-2"
        :class="[
          activeTab === tab.id
            ? 'bg-blue-50 text-[#1714EF] dark:bg-blue-950/40 dark:text-blue-400 shadow-sm'
            : 'text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/50'
        ]"
        @click="activeTab = tab.id"
      >
        <Icon :name="tab.icon" size="16" />
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <!-- Conteúdo das Abas -->
    <div class="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 p-6 md:p-8">
      <div v-show="activeTab === 'dados'">
        <StepDadosGerais
          v-model:idPropriedade="form.id_propriedade"
          v-model:dataInspecao="form.data_inspecao"
          v-model:idAuxiliar="form.id_auxiliar"
        />
      </div>

      <div v-show="activeTab === 'areas'">
        <ListAreasInspecionadas
          :areas="areas"
          @add-area="handleAddArea"
          @edit-area="handleEditArea"
          @delete-area="handleDeleteArea"
        />
      </div>

      <!-- Alertas de Validação -->
      <div v-if="validationError" class="mt-6 bg-red-50 text-red-700 text-xs px-4 py-2.5 rounded-xl border border-red-100 flex items-center gap-2">
        <Icon name="lucide:alert-circle" size="14" class="shrink-0" />
        <span>{{ validationError }}</span>
      </div>

      <!-- Botões de Navegação e Encerramento -->
      <div class="flex items-center justify-between border-t border-gray-100 dark:border-gray-800 pt-6 mt-8">
        <div>
          <BaseButton
            v-if="activeTab === 'areas'"
            variant="ghost"
            icon="lucide:arrow-left"
            @click="activeTab = 'dados'"
          >
            Passo Anterior
          </BaseButton>
        </div>
        <div class="flex gap-3">
          <BaseButton variant="ghost" @click="goBack">
            Cancelar
          </BaseButton>
          <BaseButton
            v-if="activeTab === 'dados'"
            variant="primary"
            icon="lucide:arrow-right"
            icon-position="right"
            @click="activeTab = 'areas'"
          >
            Próximo Passo
          </BaseButton>
          <BaseButton
            v-else
            variant="primary"
            icon="lucide:save"
            :loading="saving"
            @click="saveInspecao"
          >
            {{ isEditMode ? 'Salvar Alterações' : 'Concluir Inspeção' }}
          </BaseButton>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { db, offlineSave, offlineDelete, gerarIdLocal } from '~/utils/db'
import { useAuthStore } from '~/stores/auth'
import StepDadosGerais from '~/components/inspecoes/StepDadosGerais.vue'
import ListAreasInspecionadas from '~/components/inspecoes/ListAreasInspecionadas.vue'

definePageMeta({
  layout: 'default'
})

const route = useRoute()
const authStore = useAuthStore()
const paramId = route.params.id as string
const isEditMode = computed(() => paramId !== 'novo')

const activeTab = ref('dados')
const saving = ref(false)
const validationError = ref<string | null>(null)

const tabs = [
  { id: 'dados', label: '1. Dados Gerais', icon: 'lucide:file-text' },
  { id: 'areas', label: '2. Locais e Pragas', icon: 'lucide:map-pin' }
]

// Estado Principal
const form = ref({
  id_propriedade: '',
  data_inspecao: new Date().toISOString().split('T')[0],
  id_auxiliar: ''
})

const areas = ref<any[]>([])

// Lista de IDs excluídos para deletar em cascata na hora de salvar
const deletedAreaIds = ref<string[]>([])
const deletedProgramaIds = ref<string[]>([])
const deletedAmostraIds = ref<string[]>([])

// Carrega Termo para edição se aplicável
const loadInspecao = async () => {
  if (!isEditMode.value || !process.client || !db) return

  try {
    const termo = await db.termo_inspecao.get(paramId)
    if (!termo) {
      validationError.value = 'Termo de inspeção não encontrado na base de dados local.'
      return
    }

    form.value = {
      id_propriedade: termo.id_propriedade || '',
      data_inspecao: termo.data_inspecao || '',
      id_auxiliar: (termo.id_auxiliar as string) || ''
    }

    // Busca áreas físicas
    const areasLocais = await db.area_inspecionada
      .where('id_termo_inspecao')
      .equals(paramId)
      .toArray()

    const fullAreas = []
    for (const a of areasLocais) {
      // Busca programas
      const progs = await db.area_programa
        .where('id_area')
        .equals(a.id)
        .toArray()

      const fullProgs = []
      for (const p of progs) {
        // Busca amostras
        const ams = await db.amostra_coletada
          .where('id_area_programa')
          .equals(p.id)
          .toArray()

        fullProgs.push({
          ...p,
          amostras: ams
        })
      }

      fullAreas.push({
        ...a,
        programas: fullProgs
      })
    }

    areas.value = fullAreas
  } catch (err) {
    console.error('[Termo] Erro ao buscar termo:', err)
    validationError.value = 'Erro ao carregar os dados do termo para edição.'
  }
}

onMounted(() => {
  loadInspecao()
})

const goBack = () => {
  navigateTo('/inspecoes')
}

// Manipulação do estado das áreas locais
const handleAddArea = (newArea: any) => {
  areas.value.push(newArea)
}

const handleEditArea = (updatedArea: any) => {
  const idx = areas.value.findIndex(a => a.id === updatedArea.id)
  if (idx !== -1) {
    areas.value[idx] = updatedArea
  }
}

const handleDeleteArea = (areaId: string) => {
  const idx = areas.value.findIndex(a => a.id === areaId)
  if (idx !== -1) {
    const deletedArea = areas.value[idx]
    
    // Rastreia IDs deletados para posterior limpeza offlineDelete
    deletedAreaIds.value.push(areaId)
    deletedArea.programas?.forEach((p: any) => {
      deletedProgramaIds.value.push(p.id)
      p.amostras?.forEach((am: any) => {
        deletedAmostraIds.value.push(am.id)
      })
    })

    areas.value.splice(idx, 1)
  }
}

// Gravação Atômica e Validação
const saveInspecao = async () => {
  validationError.value = null

  if (!form.value.id_propriedade) {
    validationError.value = 'A propriedade rural é obrigatória.'
    activeTab.value = 'dados'
    return
  }

  if (!form.value.data_inspecao) {
    validationError.value = 'A data de inspeção é obrigatória.'
    activeTab.value = 'dados'
    return
  }

  if (areas.value.length === 0) {
    validationError.value = 'Você deve cadastrar pelo menos um local inspecionado.'
    activeTab.value = 'areas'
    return
  }

  saving.value = true

  try {
    const termoId = isEditMode.value ? paramId : gerarIdLocal()
    
    // 1. Grava Termo de Inspeção
    const termoPayload = {
      id: termoId,
      id_propriedade: form.value.id_propriedade,
      data_inspecao: form.value.data_inspecao,
      id_usuario: authStore.user?.id || '',
      id_auxiliar: form.value.id_auxiliar,
      atualizado_em: new Date().toISOString()
    }
    await offlineSave('termo_inspecao', termoPayload)

    // 2. Executa deleções rastreadas
    for (const amId of deletedAmostraIds.value) await offlineDelete('amostra_coletada', amId)
    for (const prId of deletedProgramaIds.value) await offlineDelete('area_programa', prId)
    for (const arId of deletedAreaIds.value) await offlineDelete('area_inspecionada', arId)

    // 3. Salva e atualiza as áreas físicas e dependências
    for (const area of areas.value) {
      const areaPayload = {
        id: area.id,
        id_termo_inspecao: termoId,
        tipo_area: area.tipo_area,
        nome_local: area.nome_local,
        latitude: area.latitude,
        longitude: area.longitude,
        obs: area.obs
      }
      await offlineSave('area_inspecionada', areaPayload)

      // Salva programas da área
      for (const prog of area.programas) {
        const progPayload = {
          id: prog.id,
          id_area: area.id,
          id_programa: prog.id_programa,
          especie: prog.especie,
          variedade: prog.variedade,
          material_multiplicacao: prog.material_multiplicacao,
          origem: prog.origem,
          idade_plantio: prog.idade_plantio ? Number(prog.idade_plantio) : null,
          area_plantada: prog.area_plantada ? Number(prog.area_plantada) : null,
          numero_plantas: prog.numero_plantas ? Number(prog.numero_plantas) : null,
          numero_inspecionadas: prog.numero_inspecionadas ? Number(prog.numero_inspecionadas) : null,
          numero_suspeitas: prog.numero_suspeitas ? Number(prog.numero_suspeitas) : null,
          resultado: prog.resultado,
          obs: prog.obs
        }
        await offlineSave('area_programa', progPayload)

        // Salva amostras do programa
        for (const am of (prog.amostras || [])) {
          const amostraPayload = {
            id: am.id,
            id_area_programa: prog.id,
            envelope: am.envelope,
            parte_coletada: am.parte_coletada,
            data_envio_laboratorio: am.data_envio_laboratorio,
            id_laboratorio: am.id_laboratorio,
            processo_sei: am.processo_sei,
            data_resultado: am.data_resultado,
            resultado_laboratorio: am.resultado_laboratorio
          }
          await offlineSave('amostra_coletada', amostraPayload)
        }
      }
    }

    // Sucesso, retorna
    goBack()
  } catch (err) {
    console.error('[Termo] Erro na gravação atômica:', err)
    validationError.value = 'Ocorreu um erro ao salvar a inspeção na base local.'
  } finally {
    saving.value = false
  }
}
</script>
