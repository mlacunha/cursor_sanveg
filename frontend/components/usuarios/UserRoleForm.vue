<script setup lang="ts">
import type { Usuario } from '~/types/usuario'

const props = defineProps<{
  modelValue: Partial<Usuario>
}>()

const emit = defineEmits(['update:modelValue'])

const formData = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// Mock lists for the selects
const perfis = ['ADMIN', 'TECNICO', 'EXTERNO']
const orgaos = ['MAPA - Ministério da Agricultura e Pecuária', 'ADEPARÁ - Agência de Defesa Agropecuária do Pará']
const unidades = ['SISV/DDA/SFA-PA (Belém - PA)', 'Gerência Regional de Santarém']
const cargos = ['Auditor Fiscal Federal Agropecuário - AFFA', 'Fiscal Estadual Agropecuário']
const formacoes = ['Engenheiro(a) Agrônomo(a)', 'Médico(a) Veterinário(a)', 'Técnico(a) Agrícola']
</script>

<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
    <div class="flex items-center gap-2 mb-6 text-brand-blue">
      <Icon name="lucide:shield-check" size="20" />
      <h2 class="font-bold text-slate-800">Papéis e Associações Institucionais</h2>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
      <!-- Perfil -->
      <div class="space-y-1.5">
        <label class="text-xs font-bold text-slate-500 ml-1">Permissão de Acesso (Perfil) *</label>
        <select
          v-model="formData.perfil_acesso"
          class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition-all text-sm bg-slate-50 focus:bg-white appearance-none cursor-pointer"
        >
          <option value="" disabled>Selecione um perfil</option>
          <option v-for="perfil in perfis" :key="perfil" :value="perfil">{{ perfil }}</option>
        </select>
      </div>

      <!-- Orgao -->
      <div class="space-y-1.5">
        <label class="text-xs font-bold text-slate-500 ml-1">Instituição (Órgão Vinculado) *</label>
        <select
          v-model="formData.orgao_vinculado"
          class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition-all text-sm bg-slate-50 focus:bg-white appearance-none cursor-pointer"
        >
          <option value="" disabled>Selecione o órgão</option>
          <option v-for="orgao in orgaos" :key="orgao" :value="orgao">{{ orgao }}</option>
        </select>
      </div>

      <!-- Unidade -->
      <div class="space-y-1.5">
        <label class="text-xs font-bold text-slate-500 ml-1">Unidade de Lotação</label>
        <select
          v-model="formData.unidade_lotacao"
          class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition-all text-sm bg-slate-50 focus:bg-white appearance-none cursor-pointer"
        >
          <option value="" disabled>Selecione a unidade</option>
          <option v-for="unidade in unidades" :key="unidade" :value="unidade">{{ unidade }}</option>
        </select>
      </div>

      <!-- Cargo -->
      <div class="space-y-1.5">
        <label class="text-xs font-bold text-slate-500 ml-1">Cargo do Servidor</label>
        <select
          v-model="formData.cargo"
          class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition-all text-sm bg-slate-50 focus:bg-white appearance-none cursor-pointer"
        >
          <option value="" disabled>Selecione o cargo</option>
          <option v-for="cargo in cargos" :key="cargo" :value="cargo">{{ cargo }}</option>
        </select>
      </div>

      <!-- Formacao -->
      <div class="md:col-span-2 space-y-1.5">
        <label class="text-xs font-bold text-slate-500 ml-1">Formação Acadêmica (Graduação)</label>
        <select
          v-model="formData.formacao"
          class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition-all text-sm bg-slate-50 focus:bg-white appearance-none cursor-pointer"
        >
          <option value="" disabled>Selecione a formação</option>
          <option v-for="formacao in formacoes" :key="formacao" :value="formacao">{{ formacao }}</option>
        </select>
      </div>
    </div>
  </div>
</template>
