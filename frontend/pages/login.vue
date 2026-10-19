<script setup lang="ts">
const authStore = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')

definePageMeta({
  layout: false
})

const handleLogin = async () => {
  if (!email.value || !password.value) {
    error.value = 'Por favor, preencha todos os campos.'
    return
  }

  error.value = ''
  const success = await authStore.login({
    email: email.value,
    password: password.value
  })

  if (success) {
    router.push('/')
  } else {
    error.value = authStore.error || 'Erro ao realizar login.'
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col justify-center items-center p-4">
    <div class="max-w-md w-full bg-white rounded-3xl shadow-2xl border border-slate-100 p-8">
      <!-- Header -->
      <div class="flex flex-col items-center mb-8">
        <div class="w-16 h-16 bg-Colors-BrandBlue rounded-2xl flex items-center justify-center text-white mb-4 shadow-lg shadow-Colors-BrandBlue/30">
          <Icon name="lucide:leaf" size="32" />
        </div>
        <h1 class="text-2xl font-extrabold text-slate-800">SVEGPA</h1>
        <p class="text-slate-500 font-medium mt-1 text-center">Sanidade Vegetal - Gestão de Pragas Agrícolas</p>
      </div>

      <!-- Error Alert -->
      <div v-if="error" class="mb-6 bg-red-50 text-Colors-OutbreakRed px-4 py-3 rounded-xl flex items-start gap-3 text-sm font-semibold border border-red-100 animate-in fade-in slide-in-from-top-2">
        <Icon name="lucide:alert-circle" size="18" class="mt-0.5 shrink-0" />
        <p>{{ error }}</p>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="space-y-5">
        <div class="space-y-1.5">
          <label class="text-sm font-bold text-slate-700 ml-1">Usuário (E-mail)</label>
          <div class="relative">
            <div class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400">
              <Icon name="lucide:user" size="20" />
            </div>
            <input
              v-model="email"
              type="text"
              placeholder="nome@instituicao.gov.br"
              class="w-full pl-11 pr-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:border-Colors-BrandBlue focus:ring-2 focus:ring-Colors-BrandBlue/20 transition-all font-medium text-slate-800 bg-slate-50 focus:bg-white"
            />
          </div>
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-bold text-slate-700 ml-1">Senha</label>
          <div class="relative">
            <div class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400">
              <Icon name="lucide:lock" size="20" />
            </div>
            <input
              v-model="password"
              type="password"
              placeholder="••••••••"
              class="w-full pl-11 pr-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:border-Colors-BrandBlue focus:ring-2 focus:ring-Colors-BrandBlue/20 transition-all font-medium text-slate-800 bg-slate-50 focus:bg-white"
            />
          </div>
        </div>

        <BaseButton 
          type="submit" 
          variant="primary" 
          class="w-full mt-4" 
          :loading="authStore.loading"
        >
          Acessar Plataforma
        </BaseButton>
      </form>
    </div>

    <!-- Footer -->
    <div class="mt-8 text-slate-400 text-sm font-medium">
      &copy; {{ new Date().getFullYear() }} - SIFISV/DDA/SFA-PA
    </div>
  </div>
</template>

<style scoped>
.animate-in {
  animation: animate-in 0.3s ease-out;
}

@keyframes animate-in {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
