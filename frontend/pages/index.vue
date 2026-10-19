<template>
  <div class="space-y-8">
    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">
          Olá, <span class="text-[#1714EF]">{{ authStore.user?.nome || 'Usuário' }}</span>
        </h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1 font-medium">
          {{ new Date().toLocaleDateString('pt-BR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}
        </p>
      </div>
      
      <div class="flex items-center space-x-3 bg-white dark:bg-slate-900 px-4 py-2.5 rounded-xl border border-gray-100 dark:border-gray-800 shadow-sm">
        <div class="relative flex">
          <div class="w-2.5 h-2.5 bg-green-500 rounded-full m-auto"></div>
          <div class="absolute inset-0 w-2.5 h-2.5 bg-green-500 rounded-full animate-ping opacity-75"></div>
        </div>
        <span class="text-xs font-bold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Servidor Ativo</span>
        <div class="h-4 w-px bg-gray-200 dark:bg-gray-700 mx-1"></div>
        <span class="text-xs font-medium text-gray-400">Sincronização OK</span>
      </div>
    </div>

    <!-- Quick Stats Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">
      <div v-for="(stat, index) in stats" :key="index" class="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm hover:shadow-lg hover:border-blue-100 transition-all duration-300 group">
        <div class="flex items-center justify-between mb-4">
          <div :class="`p-3 rounded-xl ${stat.bgColor} ${stat.textColor} group-hover:scale-110 transition-transform duration-300`">
            <Icon :name="stat.icon" class="w-6 h-6" />
          </div>
          <div class="flex flex-col items-end">
             <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">{{ stat.period }}</span>
             <div v-if="stat.trend !== 0" class="flex items-center mt-0.5" :class="stat.trend > 0 ? 'text-green-500' : 'text-red-500'">
                <Icon :name="stat.trend > 0 ? 'lucide:trending-up' : 'lucide:trending-down'" class="w-3 h-3 mr-0.5" />
                <span class="text-[10px] font-bold">{{ Math.abs(stat.trend) }}%</span>
             </div>
          </div>
        </div>
        <h3 class="text-sm font-semibold text-gray-400 dark:text-gray-500 mb-1 uppercase tracking-tight">{{ stat.label }}</h3>
        <p class="text-3xl font-black text-gray-900 dark:text-white tracking-tighter">{{ stat.value }}</p>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Recent Activity (Large) -->
      <div class="lg:col-span-2 bg-white dark:bg-slate-900 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm p-8">
        <div class="flex items-center justify-between mb-8">
          <div>
            <h3 class="text-lg font-bold text-gray-900 dark:text-white">Últimos Levantamentos</h3>
            <p class="text-xs text-gray-400 mt-0.5 font-medium italic">Atividades registradas nas últimas 48 horas</p>
          </div>
          <NuxtLink to="/levantamentos" class="px-4 py-2 text-xs font-bold text-[#1714EF] bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-[#1714EF] hover:text-white transition-all">
            Visualizar Todos
          </NuxtLink>
        </div>
        
        <div class="space-y-4">
          <div v-for="i in 4" :key="i" class="flex items-center p-4 rounded-xl border border-transparent hover:border-blue-50 hover:bg-slate-50 dark:hover:bg-gray-800/50 transition-all group">
            <div class="w-12 h-12 rounded-full bg-gray-50 dark:bg-gray-800 flex items-center justify-center text-gray-400 group-hover:bg-white dark:group-hover:bg-gray-700 group-hover:text-[#1714EF] shadow-sm transition-all mr-5">
              <Icon :name="i % 2 === 0 ? 'lucide:clipboard-check' : 'lucide:clipboard-warning'" class="w-5 h-5" />
            </div>
            <div class="flex-1 min-w-0">
              <h4 class="text-sm font-bold text-gray-800 dark:text-white truncate">Inspeção {{ i % 2 === 0 ? 'Citros' : 'Banana' }} - Fazenda {{ ['Boa Vista', 'Santa Maria', 'Progresso', 'Amazonia'][i-1] }}</h4>
              <p class="text-xs text-gray-500 mt-0.5">Responsável: Carlos Alberto • {{ ['Muaná', 'Castanhal', 'Belém', 'Ananindeua'][i-1] }}/PA</p>
            </div>
            <div class="flex flex-col items-end shrink-0 ml-4">
               <span class="px-2.5 py-1 rounded-md text-[10px] font-black uppercase tracking-widest mb-1 shadow-sm"
                     :class="i % 2 === 0 ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'">
                {{ i % 2 === 0 ? 'Normal' : 'Suspeita' }}
               </span>
               <span class="text-[10px] text-gray-400 font-medium">14:3{{ i }}h</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Side Cards -->
      <div class="space-y-6">
        <!-- Compact Sync Status -->
        <div class="bg-[#1714EF] rounded-2xl p-8 text-white shadow-xl shadow-blue-500/20 relative overflow-hidden group">
          <div class="relative z-10 flex flex-col h-full justify-between">
            <div>
              <Icon name="lucide:refresh-cw" class="w-8 h-8 mb-4 opacity-80 group-hover:rotate-180 transition-transform duration-700" />
              <h3 class="text-xl font-bold mb-2">Sincronização</h3>
              <p class="text-blue-100/70 text-sm leading-relaxed">Sua base de dados está 100% atualizada com a nuvem.</p>
            </div>
            <div class="mt-8 flex items-end justify-between">
              <span class="text-4xl font-black">0</span>
              <span class="text-xs font-bold uppercase tracking-widest text-blue-200">Pendentes</span>
            </div>
          </div>
          <!-- Decorative Pattern -->
          <div class="absolute -right-4 -bottom-4 opacity-10">
            <Icon name="lucide:cloud-upload" class="w-32 h-32" />
          </div>
        </div>

        <!-- System Alerts / Health -->
        <div class="bg-white dark:bg-slate-900 rounded-2xl border border-gray-100 dark:border-gray-800 shadow-sm p-6">
          <h3 class="text-sm font-bold text-gray-900 dark:text-white mb-4 uppercase tracking-wider">Alertas Regionais</h3>
          <div class="space-y-3">
            <div class="flex items-start space-x-3 p-3 bg-amber-50 dark:bg-amber-900/10 rounded-lg">
              <Icon name="lucide:alert-circle" class="w-4 h-4 text-amber-600 mt-0.5" />
              <p class="text-[11px] text-amber-800 dark:text-amber-300 leading-tight">Atenção redobrada na região de Castanhal devido ao clima úmido.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Força o layout `default` (com Sidebar); `meta.layout === false` omite o shell no NuxtLayout.
definePageMeta({
  layout: 'default',
})

const authStore = useAuthStore()

const stats = [
  {
    label: 'Total de Inspeções',
    value: '1.248',
    icon: 'lucide:clipboard-list',
    bgColor: 'bg-blue-50 dark:bg-blue-900/10',
    textColor: 'text-blue-600',
    period: 'Este mês',
    trend: 12,
    trendText: '+12% em relação ao mês anterior'
  },
  {
    label: 'Propriedades Ativas',
    value: '452',
    icon: 'lucide:home',
    bgColor: 'bg-green-50 dark:bg-green-900/10',
    textColor: 'text-green-600',
    period: 'Total',
    trend: 5,
    trendText: '+5 novas propriedades'
  },
  {
    label: 'Alertas Sanitários',
    value: '3',
    icon: 'lucide:alert-triangle',
    bgColor: 'bg-red-50 dark:bg-red-900/10',
    textColor: 'text-red-600',
    period: 'Últimas 24h',
    trend: 0,
    trendText: 'Estável'
  },
  {
    label: 'Agentes em Campo',
    value: '18',
    icon: 'lucide:users',
    bgColor: 'bg-purple-50 dark:bg-purple-900/10',
    textColor: 'text-purple-600',
    period: 'Agora',
    trend: 2,
    trendText: 'Sincronizando agora'
  }
]
</script>
