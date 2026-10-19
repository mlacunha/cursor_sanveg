<script setup lang="ts">
import { useUsuarios } from '~/composables/useUsuarios'
import type { Usuario } from '~/types/usuario'

const route = useRoute()
const { getUsuarioById } = useUsuarios()

const id = route.params.id as string
const isNovo = id === 'novo'
const loading = ref(false)

const usuario = ref<Partial<Usuario>>({
  ativo: true,
  perfil_acesso: 'TECNICO'
})

onMounted(() => {
  if (!isNovo) {
    const data = getUsuarioById(id)
    if (data) {
      usuario.value = { ...data }
    }
  }
})

const voltar = () => navigateTo('/usuarios')

const salvar = async () => {
  loading.value = true
  // Simular delay de rede
  await new Promise(resolve => setTimeout(resolve, 800))
  loading.value = false
  
  // No mundo real, aqui chamaria o store/API
  navigateTo('/usuarios')
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col">
    <!-- Header -->
    <DetailHeader 
      :title="isNovo ? 'Novo Usuário' : 'Editar Usuário'"
      :subtitle="isNovo ? 'Cadastre um novo servidor ou colaborador no sistema' : usuario.nome"
      :loading="loading"
      @back="voltar"
      @save="salvar"
    />

    <!-- Main Content -->
    <main class="flex-1 p-4 md:p-8 max-w-5xl mx-auto w-full pb-32">
      <div class="space-y-6">
        <!-- Grid de Formulários -->
        <div class="grid grid-cols-1 gap-6">
          <UsuariosUserPersonalForm v-model="usuario" />
          <UsuariosUserRoleForm v-model="usuario" />
        </div>

        <!-- Status Card -->
        <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center text-slate-500">
                <Icon name="lucide:power" size="20" />
              </div>
              <div>
                <h3 class="font-bold text-slate-800">Status da Conta</h3>
                <p class="text-xs text-slate-500">Usuários inativos não podem acessar a plataforma</p>
              </div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" v-model="usuario.ativo" class="sr-only peer">
              <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-brand-blue"></div>
              <span class="ms-3 text-sm font-medium text-slate-700">{{ usuario.ativo ? 'Ativo' : 'Inativo' }}</span>
            </label>
          </div>
        </div>
      </div>
    </main>

    <!-- Sticky Footer - Mobile First Visibility -->
    <footer class="fixed bottom-0 left-0 right-0 z-40 bg-white/80 backdrop-blur-md border-t border-slate-200 px-6 py-4 shadow-[0_-4px_20px_0_rgba(0,0,0,0.05)] md:hidden">
      <div class="flex items-center gap-3">
        <BaseButton 
          variant="outline" 
          class="flex-1"
          @click="voltar"
        >
          Cancelar
        </BaseButton>
        <BaseButton 
          variant="primary" 
          class="flex-1"
          :loading="loading"
          @click="salvar"
        >
          Salvar
        </BaseButton>
      </div>
    </footer>
    
    <!-- Footer Desktop (Opcional, mas solicitado como sticky footer) -->
    <footer class="hidden md:block fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-slate-200 px-8 py-4 shadow-[0_-4px_20px_0_rgba(0,0,0,0.05)] transform transition-transform duration-300">
      <div class="max-w-5xl mx-auto flex items-center justify-between">
        <div class="flex items-center gap-2 text-slate-400 text-sm">
          <Icon name="lucide:info" size="16" />
          <span>Campos marcados com * são obrigatórios</span>
        </div>
        <div class="flex items-center gap-3">
          <BaseButton 
            variant="outline" 
            @click="voltar"
          >
            Descartar Alterações
          </BaseButton>
          <BaseButton 
            variant="primary" 
            :loading="loading"
            @click="salvar"
          >
            Confirmar e Salvar
          </BaseButton>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Garante que o conteúdo não fique escondido sob o footer fixo */
main {
  padding-bottom: 7rem; /* Aproximadamente o dobro da altura do footer */
}
</style>
