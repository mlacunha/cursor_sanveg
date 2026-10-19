<template>
  <div class="p-8 space-y-6 bg-slate-50/50 dark:bg-slate-900/50">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Código -->
      <div class="space-y-2">
        <label class="text-sm font-bold text-gray-700 dark:text-gray-300">Código do Programa</label>
        <input 
          v-model="modelValue.codigo" 
          type="text" 
          placeholder="Ex: PNVF"
          class="w-full px-4 py-3 bg-white dark:bg-slate-800 border border-gray-200 dark:border-gray-700 rounded-2xl outline-none focus:ring-2 focus:ring-[#1714EF]/20 focus:border-[#1714EF] transition-all font-mono"
        />
      </div>

      <!-- Nome -->
      <div class="space-y-2">
        <label class="text-sm font-bold text-gray-700 dark:text-gray-300">Nome Oficial *</label>
        <input 
          v-model="modelValue.nome" 
          type="text" 
          required
          placeholder="Nome completo do programa"
          class="w-full px-4 py-3 bg-white dark:bg-slate-800 border border-gray-200 dark:border-gray-700 rounded-2xl outline-none focus:ring-2 focus:ring-[#1714EF]/20 focus:border-[#1714EF] transition-all"
        />
      </div>

      <!-- Nome Científico (Alvo) -->
      <div class="space-y-2">
        <label class="text-sm font-bold text-gray-700 dark:text-gray-300">Organismo Alvo (Científico)</label>
        <div class="relative">
          <input 
            v-model="modelValue.nome_cientifico" 
            type="text" 
            placeholder="Ex: Candidatus Liberibacter"
            class="w-full px-4 py-3 bg-white dark:bg-slate-800 border border-gray-200 dark:border-gray-700 rounded-2xl outline-none focus:ring-2 focus:ring-[#1714EF]/20 focus:border-[#1714EF] transition-all italic"
          />
          <Icon name="lucide:microscope" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
        </div>
      </div>

      <!-- Nomes Comuns -->
      <div class="space-y-2">
        <label class="text-sm font-bold text-gray-700 dark:text-gray-300">Nomes Comuns / Sinônimos</label>
        <input 
          v-model="modelValue.nomes_comuns" 
          type="text" 
          placeholder="Ex: Greening, Amarelão"
          class="w-full px-4 py-3 bg-white dark:bg-slate-800 border border-gray-200 dark:border-gray-700 rounded-2xl outline-none focus:ring-2 focus:ring-[#1714EF]/20 focus:border-[#1714EF] transition-all"
        />
      </div>
    </div>

    <!-- Descrição Adicional -->
    <div class="space-y-2">
      <label class="text-sm font-bold text-gray-700 dark:text-gray-300">Observações Estratégicas</label>
      <textarea 
        v-model="modelValue.descricao"
        rows="3"
        placeholder="Detalhes sobre a abrangência ou objetivos do programa..."
        class="w-full px-4 py-3 bg-white dark:bg-slate-800 border border-gray-200 dark:border-gray-700 rounded-2xl outline-none focus:ring-2 focus:ring-[#1714EF]/20 focus:border-[#1714EF] transition-all resize-none"
      ></textarea>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: {
    codigo: string
    nome: string
    nome_cientifico: string
    nomes_comuns: string
    descricao?: string
  }
}>()
</script>
