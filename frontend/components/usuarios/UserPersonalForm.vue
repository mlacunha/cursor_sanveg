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
</script>

<template>
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
    <div class="flex items-center gap-2 mb-6 text-brand-blue">
      <Icon name="lucide:user-circle" size="20" />
      <h2 class="font-bold text-slate-800">Dados Pessoais de Acesso</h2>
    </div>

    <!-- Responsive Grid: 1 col on mobile, 2 cols on md+ -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
      <!-- Nome -->
      <div class="md:col-span-2 space-y-1.5">
        <label class="text-xs font-bold text-slate-500 ml-1">Nome Completo *</label>
        <input
          v-model="formData.nome"
          type="text"
          placeholder="Digite o nome completo"
          class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition-all text-sm bg-slate-50 focus:bg-white"
        />
      </div>

      <!-- Email -->
      <div class="space-y-1.5">
        <label class="text-xs font-bold text-slate-500 ml-1">E-mail *</label>
        <input
          v-model="formData.email"
          type="email"
          placeholder="exemplo@agro.gov.br"
          class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition-all text-sm bg-slate-50 focus:bg-white"
        />
      </div>

      <!-- Telefone -->
      <div class="space-y-1.5">
        <label class="text-xs font-bold text-slate-500 ml-1">Telefone</label>
        <input
          v-model="formData.telefone"
          type="text"
          placeholder="(00) 00000-0000"
          class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition-all text-sm bg-slate-50 focus:bg-white"
        />
      </div>

      <!-- CPF -->
      <div class="space-y-1.5">
        <label class="text-xs font-bold text-slate-500 ml-1">CPF *</label>
        <input
          v-model="formData.cpf"
          type="text"
          placeholder="000.000.000-00"
          class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition-all text-sm bg-slate-50 focus:bg-white"
        />
      </div>

      <!-- Matricula -->
      <div class="space-y-1.5">
        <label class="text-xs font-bold text-slate-500 ml-1">Matrícula</label>
        <input
          v-model="formData.matricula"
          type="text"
          placeholder="0000000"
          class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition-all text-sm bg-slate-50 focus:bg-white"
        />
      </div>

      <!-- Carteira Fiscal -->
      <div class="space-y-1.5">
        <label class="text-xs font-bold text-slate-500 ml-1">Carteira Fiscal</label>
        <input
          v-model="formData.carteira_fiscal"
          type="text"
          placeholder="CF 0000000"
          class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition-all text-sm bg-slate-50 focus:bg-white"
        />
      </div>

      <!-- Senha -->
      <div class="space-y-1.5">
        <label class="text-xs font-bold text-slate-500 ml-1">Senha / Credencial</label>
        <input
          v-model="formData.senha"
          type="password"
          placeholder="••••••••"
          class="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/20 transition-all text-sm bg-slate-50 focus:bg-white"
        />
      </div>

      <!-- Ativo -->
      <div class="md:col-span-2 flex items-center gap-2 pt-2">
        <input
          id="is_active"
          v-model="formData.ativo"
          type="checkbox"
          class="w-4 h-4 text-brand-blue border-gray-300 rounded focus:ring-brand-blue/20"
        />
        <label for="is_active" class="text-sm font-bold text-slate-700 select-none cursor-pointer">
          Permitir Login (Usuário Ativo)
        </label>
      </div>
    </div>
  </div>
</template>
