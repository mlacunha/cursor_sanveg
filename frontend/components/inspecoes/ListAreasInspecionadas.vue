<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-lg font-bold text-gray-800 dark:text-white">2. Locais e Pragas Monitoradas</h2>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">Adicione os talhões inspecionados, avaliações de pragas e amostras coletadas</p>
      </div>
      <BaseButton
        variant="primary"
        size="sm"
        icon="lucide:plus"
        @click="openAreaModal()"
      >
        Adicionar Local
      </BaseButton>
    </div>

    <!-- Lista de Áreas / Talhões -->
    <div v-if="areas.length === 0" class="flex flex-col items-center justify-center p-12 bg-gray-50 dark:bg-slate-900/50 rounded-2xl border border-dashed border-gray-200 dark:border-gray-800 text-gray-400">
      <Icon name="lucide:map" size="48" class="mb-4 text-gray-300" />
      <span class="text-sm font-semibold">Nenhum local físico cadastrado neste termo</span>
      <p class="text-xs text-gray-500 mt-1">Clique em "Adicionar Local" para inserir um talhão ou viveiro</p>
    </div>

    <div v-else class="grid grid-cols-1 gap-6">
      <div
        v-for="area in areas"
        :key="area.id"
        class="bg-gray-50 dark:bg-slate-900/40 p-6 rounded-2xl border border-gray-100 dark:border-gray-800/80 shadow-sm relative hover:shadow-md transition-all group"
      >
        <!-- Topo da Área -->
        <div class="flex items-start justify-between mb-4 border-b border-gray-200/50 dark:border-gray-800/60 pb-3">
          <div class="flex items-start gap-3">
            <div class="p-2 bg-blue-50 dark:bg-blue-950/20 text-[#1714EF] rounded-xl">
              <Icon name="lucide:map-pin" size="20" />
            </div>
            <div>
              <h3 class="font-bold text-gray-800 dark:text-white text-base">{{ area.nome_local }}</h3>
              <p class="text-xs text-gray-500 mt-0.5 capitalize">
                {{ formatTipoArea(area.tipo_area) }}
                <span v-if="area.latitude && area.longitude">
                  • GPS: {{ Number(area.latitude).toFixed(4) }}, {{ Number(area.longitude).toFixed(4) }}
                </span>
              </p>
            </div>
          </div>
          <!-- Ações da Área -->
          <div class="flex gap-2">
            <BaseButton
              variant="ghost"
              size="icon"
              icon="lucide:edit-2"
              class="text-slate-400 hover:text-[#1714EF]"
              title="Editar Área"
              @click="openAreaModal(area)"
            />
            <BaseButton
              variant="ghost"
              size="icon"
              icon="lucide:trash-2"
              class="text-slate-400 hover:text-red-500"
              title="Excluir Área"
              @click="$emit('delete-area', area.id)"
            />
          </div>
        </div>

        <!-- Lista de Pragas Inspecionadas nesta Área -->
        <div class="space-y-4 pl-0 md:pl-10">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-gray-400 uppercase tracking-widest">Inspeção de Pragas</span>
            <BaseButton
              variant="ghost"
              size="sm"
              icon="lucide:plus"
              class="text-xs font-bold text-[#1714EF] hover:bg-blue-50"
              @click="openProgModal(area.id)"
            >
              Adicionar Praga
            </BaseButton>
          </div>

          <div v-if="!area.programas || area.programas.length === 0" class="text-xs text-gray-400 italic">
            Nenhuma praga ou programa sanitário avaliado neste local.
          </div>

          <div v-else class="grid grid-cols-1 gap-3">
            <div
              v-for="prog in area.programas"
              :key="prog.id"
              class="bg-white dark:bg-slate-900 border border-gray-100 dark:border-gray-800/80 p-4 rounded-xl shadow-sm flex flex-col md:flex-row justify-between gap-4"
            >
              <div class="space-y-2 flex-1">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="font-bold text-sm text-gray-800 dark:text-white">{{ getProgramaName(prog.id_programa) }}</span>
                  <span
                    class="px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-wider"
                    :class="getStatusClass(prog.resultado)"
                  >
                    {{ prog.resultado }}
                  </span>
                </div>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-x-4 gap-y-1 text-xs text-gray-500">
                  <span v-if="prog.especie"><b>Espécie:</b> {{ prog.especie }}</span>
                  <span v-if="prog.variedade"><b>Var:</b> {{ prog.variedade }}</span>
                  <span><b>Insp:</b> {{ prog.numero_inspecionadas }}</span>
                  <span :class="{ 'text-red-500 font-bold': prog.numero_suspeitas > 0 }">
                    <b>Susp:</b> {{ prog.numero_suspeitas }}
                  </span>
                </div>
                <p v-if="prog.obs" class="text-xs text-gray-400 italic">"{{ prog.obs }}"</p>

                <!-- Amostras Coletadas para esta Praga -->
                <div v-if="prog.amostras && prog.amostras.length > 0" class="mt-3 border-t border-gray-100 dark:border-gray-800 pt-3">
                  <div class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">Amostras Laboratoriais</div>
                  <div class="space-y-2">
                    <div
                      v-for="am in prog.amostras"
                      :key="am.id"
                      class="bg-slate-50 dark:bg-slate-950/40 p-2.5 rounded-lg border border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs"
                    >
                      <div class="flex items-center gap-2">
                        <Icon name="lucide:flask-conical" class="text-purple-500" size="14" />
                        <div>
                          <span class="font-bold text-gray-700 dark:text-gray-300">Envelope: {{ am.envelope }}</span>
                          <span class="text-gray-400 mx-1.5">•</span>
                          <span class="text-gray-500">Parte: {{ am.parte_coletada }}</span>
                          <span v-if="am.processo_sei" class="text-gray-500 ml-2">(SEI: {{ am.processo_sei }})</span>
                        </div>
                      </div>
                      <div class="flex gap-1.5">
                        <button @click="openAmostraModal(prog.id, am)" class="text-slate-400 hover:text-[#1714EF]">Editar</button>
                        <button @click="deleteAmostra(area.id, prog.id, am.id)" class="text-slate-400 hover:text-red-500">Excluir</button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Ações do Programa -->
              <div class="flex md:flex-col items-end justify-between md:justify-start gap-2 border-t md:border-t-0 border-gray-100 pt-3 md:pt-0">
                <div class="flex gap-2">
                  <BaseButton
                    variant="ghost"
                    size="icon"
                    icon="lucide:edit-2"
                    class="text-xs text-slate-400 hover:text-[#1714EF]"
                    title="Editar Praga"
                    @click="openProgModal(area.id, prog)"
                  />
                  <BaseButton
                    variant="ghost"
                    size="icon"
                    icon="lucide:trash-2"
                    class="text-xs text-slate-400 hover:text-red-500"
                    title="Excluir Praga"
                    @click="deletePrograma(area.id, prog.id)"
                  />
                </div>
                <!-- Botão de Coleta de Amostra (se suspeita ou positivo) -->
                <BaseButton
                  v-if="prog.resultado === 'SUSPEITA' || prog.resultado === 'POSITIVO'"
                  variant="ghost"
                  size="sm"
                  icon="lucide:flask-conical"
                  class="text-xs font-bold text-purple-600 bg-purple-50 hover:bg-purple-100 border border-purple-100"
                  @click="openAmostraModal(prog.id)"
                >
                  Adicionar Amostra
                </BaseButton>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modais Internos -->
    <!-- 1. Modal Área Física -->
    <ModalAreaInspecionada
      v-if="showAreaModal"
      :initial-data="editingArea"
      :is-edit="!!editingArea"
      @close="showAreaModal = false"
      @submit="submitArea"
    />

    <!-- 2. Modal Programa/Praga -->
    <ModalAreaPrograma
      v-if="showProgModal"
      :initial-data="editingProg"
      :is-edit="!!editingProg"
      @close="showProgModal = false"
      @submit="submitPrograma"
    />

    <!-- 3. Modal Amostra -->
    <ModalAmostraColetada
      v-if="showAmostraModal"
      :initial-data="editingAmostra"
      :is-edit="!!editingAmostra"
      @close="showAmostraModal = false"
      @submit="submitAmostra"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { db, type Programa } from '~/utils/db'
import ModalAreaInspecionada from '~/components/inspecoes/ModalAreaInspecionada.vue'
import ModalAreaPrograma from '~/components/inspecoes/ModalAreaPrograma.vue'
import ModalAmostraColetada from '~/components/inspecoes/ModalAmostraColetada.vue'

const props = defineProps<{
  areas: any[]
}>()

const emit = defineEmits(['add-area', 'edit-area', 'delete-area'])

const programas = ref<Programa[]>([])

const loadProgramas = async () => {
  if (process.client && db) {
    programas.value = await db.programas.toArray()
  }
}

onMounted(() => {
  loadProgramas()
})

const getProgramaName = (id: string) => {
  return programas.value.find(p => p.id === id)?.nome || 'Programa N/A'
}

const formatTipoArea = (val: string) => {
  return {
    pomar_comercial: 'Pomar Comercial',
    viveiro: 'Viveiro / Estufa',
    plantiu_domestico: 'Plantio Doméstico',
    area_silvestre: 'Área Silvestre / Mata',
    outro: 'Outro'
  }[val] || val
}

const getStatusClass = (res: string) => {
  if (res === 'POSITIVO' || res === 'FOCO') return 'bg-red-100 text-red-700'
  if (res === 'SUSPEITA') return 'bg-amber-100 text-amber-700'
  return 'bg-blue-100 text-blue-700'
}

// -----------------------------------------------------------------------------
// Gerenciamento de Modal 1: Área Física
// -----------------------------------------------------------------------------
const showAreaModal = ref(false)
const editingArea = ref<any | null>(null)

const openAreaModal = (area?: any) => {
  editingArea.value = area ? { ...area } : null
  showAreaModal.value = true
}

const submitArea = (area: any) => {
  showAreaModal.value = false
  if (editingArea.value) {
    emit('edit-area', area)
  } else {
    emit('add-area', area)
  }
}

// -----------------------------------------------------------------------------
// Gerenciamento de Modal 2: Programa Fitossanitário (Praga)
// -----------------------------------------------------------------------------
const showProgModal = ref(false)
const editingProg = ref<any | null>(null)
const currentAreaIdForProg = ref<string | null>(null)

const openProgModal = (areaId: string, prog?: any) => {
  currentAreaIdForProg.value = areaId
  editingProg.value = prog ? { ...prog } : null
  showProgModal.value = true
}

const submitPrograma = (prog: any) => {
  showProgModal.value = false
  const areaId = currentAreaIdForProg.value
  if (!areaId) return

  const area = props.areas.find(a => a.id === areaId)
  if (area) {
    const updatedArea = { ...area }
    updatedArea.programas = updatedArea.programas ? [...updatedArea.programas] : []

    if (editingProg.value) {
      const idx = updatedArea.programas.findIndex((p: any) => p.id === prog.id)
      if (idx !== -1) updatedArea.programas[idx] = prog
    } else {
      updatedArea.programas.push(prog)
    }
    emit('edit-area', updatedArea)
  }
}

const deletePrograma = (areaId: string, progId: string) => {
  const area = props.areas.find(a => a.id === areaId)
  if (area) {
    const updatedArea = { ...area }
    updatedArea.programas = updatedArea.programas.filter((p: any) => p.id !== progId)
    emit('edit-area', updatedArea)
  }
}

// -----------------------------------------------------------------------------
// Gerenciamento de Modal 3: Amostra Coletada
// -----------------------------------------------------------------------------
const showAmostraModal = ref(false)
const editingAmostra = ref<any | null>(null)
const currentProgIdForAmostra = ref<string | null>(null)

const openAmostraModal = (progId: string, amostra?: any) => {
  currentProgIdForAmostra.value = progId
  editingAmostra.value = amostra ? { ...amostra } : null
  showAmostraModal.value = true
}

const submitAmostra = (amostra: any) => {
  showAmostraModal.value = false
  const progId = currentProgIdForAmostra.value
  if (!progId) return

  // Encontra a área que contém esse programa
  let targetArea: any = null
  let targetProg: any = null

  for (const area of props.areas) {
    const p = area.programas?.find((p: any) => p.id === progId)
    if (p) {
      targetArea = area
      targetProg = p
      break
    }
  }

  if (targetArea && targetProg) {
    const updatedArea = { ...targetArea }
    const progIndex = updatedArea.programas.findIndex((p: any) => p.id === progId)
    
    // Clona o programa e a lista de amostras
    const updatedProg = { ...targetProg }
    updatedProg.amostras = updatedProg.amostras ? [...updatedProg.amostras] : []

    if (editingAmostra.value) {
      const idx = updatedProg.amostras.findIndex((am: any) => am.id === amostra.id)
      if (idx !== -1) updatedProg.amostras[idx] = amostra
    } else {
      updatedProg.amostras.push(amostra)
    }

    updatedArea.programas[progIndex] = updatedProg
    emit('edit-area', updatedArea)
  }
}

const deleteAmostra = (areaId: string, progId: string, amostraId: string) => {
  const area = props.areas.find(a => a.id === areaId)
  if (area) {
    const updatedArea = { ...area }
    const progIndex = updatedArea.programas.findIndex((p: any) => p.id === progId)
    const prog = updatedArea.programas[progIndex]
    
    const updatedProg = { ...prog }
    updatedProg.amostras = updatedProg.amostras.filter((am: any) => am.id !== amostraId)
    
    updatedArea.programas[progIndex] = updatedProg
    emit('edit-area', updatedArea)
  }
}
</script>
