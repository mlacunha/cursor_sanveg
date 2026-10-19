<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950">
    <!-- Componente de Cabeçalho Sticky -->
    <DetailHeader 
      :title="programa.nome || 'Carregando Programa...'"
      :subtitle="programa.codigo ? `Código: ${programa.codigo}` : 'ID: ' + $route.params.id"
      :loading="submitting"
      @back="navigateTo('/cadastro/programas')"
      @save="handleSave"
    />

    <main class="p-6 max-w-7xl mx-auto">
      <div class="bg-white dark:bg-slate-900 rounded-3xl shadow-xl shadow-slate-200/50 dark:shadow-none border border-gray-100 dark:border-gray-800 overflow-hidden">
        <!-- Componente de Abas -->
        <BaseTabs 
          v-model="activeTab" 
          :tabs="[
            { label: 'Dados Gerais', value: 'geral', icon: 'lucide:info' },
            { label: 'Hospedeiros', value: 'hospedeiros', icon: 'lucide:leaf' },
            { label: 'Normas', value: 'normas', icon: 'lucide:scroll-text' }
          ]" 
        />

        <!-- Conteúdo Dinâmico (Componentes Atômicos) -->
        <div class="min-h-[400px]">
          <transition name="fade" mode="out-in">
            <div :key="activeTab">
              <!-- Aba 1: Dados Gerais -->
              <ProgramForm 
                v-if="activeTab === 'geral'" 
                v-model="programa" 
              />

              <!-- Aba 2: Hospedeiros -->
              <HostTable 
                v-else-if="activeTab === 'hospedeiros'" 
                :hosts="hospedeiros" 
              />

              <!-- Aba 3: Normas -->
              <NormsTable 
                v-else-if="activeTab === 'normas'" 
                :norms="normas" 
              />
            </div>
          </transition>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import ProgramForm from '~/components/programs/ProgramForm.vue'
import HostTable from '~/components/programs/HostTable.vue'
import NormsTable from '~/components/programs/NormsTable.vue'

const route = useRoute()
const activeTab = ref('geral')
const submitting = ref(false)

// Estado do Programa (Inicia com dados para Modo Demo se necessário)
const programa = ref({
  id: String(route.params.id),
  codigo: route.params.id === '1' ? 'PNVF' : 'HLB',
  nome: route.params.id === '1' ? 'Programa Nacional de Vigilância Fitossanitária' : 'Controle do Greening',
  nome_cientifico: route.params.id === '1' ? '-' : 'Candidatus Liberibacter',
  nomes_comuns: route.params.id === '1' ? 'Vigilância' : 'Greening, HLB',
  descricao: ''
})

// Mock Data para Hospedeiros
const hospedeiros = ref([
  { id: '1', nome: 'Citros (Laranja, Limão, Tangerina)', nome_cientifico: 'Citrus spp.' },
  { id: '2', nome: 'Murta de Jardim', nome_cientifico: 'Murraya paniculata' }
])

// Mock Data para Normas
const normas = ref([
  { id: '1', numero: 'Portaria SDA nº 317/2021', ementa: 'Estabelece as normas para a certificação fitossanitária de origem.', tipo: 'Portaria', data: '22/05/2021' },
  { id: '2', numero: 'Instrução Normativa nº 53/2008', ementa: 'Critérios e procedimentos para a aplicação de medidas fitossanitárias.', tipo: 'I.N.', data: '10/11/2008' }
])

const handleSave = () => {
  submitting.value = true
  setTimeout(() => {
    submitting.value = false
    alert('Alterações salvas com sucesso (Simulação)')
  }, 1000)
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
