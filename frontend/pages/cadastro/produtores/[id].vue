<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Header de Detalhes -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 dark:text-white">
          {{ isEditMode ? 'Editar Produtor' : 'Novo Produtor' }}
        </h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {{ isEditMode ? 'Atualize as informações do produtor selecionado' : 'Preencha os campos abaixo para cadastrar um novo produtor agropecuário' }}
        </p>
      </div>
      
      <BaseButton variant="ghost" icon="lucide:arrow-left" @click="goBack">
        Voltar
      </BaseButton>
    </div>

    <!-- Card de Formulário -->
    <div class="bg-white dark:bg-slate-900 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-800 p-6 md:p-8">
      <form @submit.prevent="submitForm" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Nome / Razão Social -->
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Nome / Razão Social <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.nome"
              type="text"
              required
              maxlength="100"
              placeholder="Digite o nome completo ou razão social"
              class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <!-- CPF / CNPJ -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              CPF / CNPJ <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.cpf_cnpj"
              type="text"
              required
              placeholder="000.000.000-00 ou 00.000.000/0000-00"
              class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <!-- Inscrição Estadual -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Inscrição Estadual
            </label>
            <input
              v-model="form.inscricao_estadual"
              type="text"
              placeholder="Inscrição Estadual se houver"
              class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <!-- E-mail -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              E-mail
            </label>
            <input
              v-model="form.email"
              type="email"
              placeholder="nome@exemplo.com"
              class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <!-- Telefone -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Telefone
            </label>
            <input
              v-model="form.telefone"
              type="text"
              placeholder="(00) 00000-0000"
              class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <!-- Endereço -->
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Endereço Residencial/Comercial
            </label>
            <input
              v-model="form.endereco"
              type="text"
              placeholder="Rua, número, bairro, cidade - UF"
              class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
            />
          </div>
        </div>

        <!-- Alertas de Validação -->
        <div v-if="validationError" class="bg-red-50 text-red-700 text-xs px-4 py-2.5 rounded-xl border border-red-100 flex items-center gap-2">
          <Icon name="lucide:alert-circle" size="14" class="shrink-0" />
          <span>{{ validationError }}</span>
        </div>

        <!-- Botões de Ação -->
        <div class="flex items-center justify-end gap-3 border-t border-gray-100 dark:border-gray-800 pt-6">
          <BaseButton variant="ghost" type="button" @click="goBack">
            Cancelar
          </BaseButton>
          <BaseButton variant="primary" type="submit" :loading="saving">
            {{ isEditMode ? 'Salvar Alterações' : 'Cadastrar Produtor' }}
          </BaseButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { db, type Produtor, offlineSave, gerarIdLocal } from '~/utils/db'

const route = useRoute()
const paramId = route.params.id as string

const isEditMode = computed(() => paramId !== 'novo')

const form = ref<Partial<Produtor>>({
  nome: '',
  cpf_cnpj: '',
  inscricao_estadual: '',
  email: '',
  telefone: '',
  endereco: ''
})

const saving = ref(false)
const validationError = ref<string | null>(null)

// Carrega dados do produtor se estiver no modo de edição
const loadProducer = async () => {
  if (isEditMode.value && process.client && db) {
    try {
      const data = await db.produtores.get(paramId)
      if (data) {
        form.value = { ...data }
      } else {
        validationError.value = 'Produtor não encontrado na base de dados local.'
      }
    } catch (err) {
      console.error('[Produtores] Erro ao buscar produtor:', err)
      validationError.value = 'Erro ao carregar dados do registro local.'
    }
  }
}

onMounted(() => {
  loadProducer()
})

const goBack = () => {
  navigateTo('/cadastro/produtores')
}

// Submissão do Formulário com Validação Offline
const submitForm = async () => {
  validationError.value = null
  
  // Validações básicas no lado do cliente
  if (!form.value.nome || form.value.nome.trim().length < 3) {
    validationError.value = 'O nome ou razão social deve ter pelo menos 3 caracteres.'
    return
  }

  if (!form.value.cpf_cnpj) {
    validationError.value = 'O campo CPF / CNPJ é obrigatório.'
    return
  }

  // Remove formatação para validação simples de comprimento
  const cleanCpfCnpj = form.value.cpf_cnpj.replace(/\D/g, '')
  if (cleanCpfCnpj.length !== 11 && cleanCpfCnpj.length !== 14) {
    validationError.value = 'O CPF/CNPJ informado é inválido. Digite 11 dígitos para CPF ou 14 para CNPJ.'
    return
  }

  saving.value = true

  try {
    const finalData = { ...form.value }
    
    // Se for criação de novo registro, gera o UUID local compatível com VARCHAR(36)
    if (!isEditMode.value) {
      finalData.id = gerarIdLocal()
    }

    // Grava localmente e agenda sincronismo de push
    await offlineSave('produtores', finalData as Record<string, unknown>)
    
    // Sucesso, retorna à página de listagem
    goBack()
  } catch (err) {
    console.error('[Produtores] Erro ao persistir dados localmente:', err)
    validationError.value = 'Falha crítica ao gravar dados locais no IndexedDB.'
  } finally {
    saving.value = false
  }
}
</script>
