<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Header de Detalhes -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-800 dark:text-white">
          {{ isEditMode ? 'Editar Propriedade' : 'Nova Propriedade' }}
        </h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {{ isEditMode ? 'Atualize as informações da propriedade rural selecionada' : 'Preencha os campos abaixo para cadastrar uma nova propriedade rural' }}
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
          <!-- Nome da Propriedade -->
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Nome da Propriedade <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.nome"
              type="text"
              required
              maxlength="100"
              placeholder="Ex: Fazenda Santa Maria"
              class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <!-- Produtor Responsável (Vínculo Obrigatório) -->
          <div class="md:col-span-2">
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Produtor Agropecuário Responsável <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.id_produtor"
              required
              class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
            >
              <option value="" disabled>Selecione o proprietário/responsável...</option>
              <option
                v-for="prod in producers"
                :key="prod.id"
                :value="prod.id"
              >
                {{ prod.nome }} - ({{ prod.cpf_cnpj || 'Sem CPF/CNPJ' }})
              </option>
            </select>
            <p v-if="producers.length === 0" class="text-xs text-amber-500 mt-1 flex items-center gap-1">
              <Icon name="lucide:alert-triangle" size="12" />
              <span>Nenhum produtor cadastrado localmente. Cadastre um produtor antes de criar propriedades.</span>
            </p>
          </div>

          <!-- Município -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Município <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.municipio"
              type="text"
              required
              placeholder="Digite o município da propriedade"
              class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <!-- Cadastro Ambiental Rural (CAR) -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Número do CAR
            </label>
            <input
              v-model="form.car_numero"
              type="text"
              placeholder="Ex: PA-1505802-3D28..."
              class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <!-- Código INCRA -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Código INCRA
            </label>
            <input
              v-model="form.codigo_incra"
              type="text"
              placeholder="Código de registro no INCRA"
              class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <!-- Área Total (ha) -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Área Total (Hectares)
            </label>
            <input
              v-model="form.area_total"
              type="number"
              step="0.01"
              placeholder="Ex: 150.50"
              class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <!-- Latitude -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Latitude (Sede)
            </label>
            <input
              v-model="form.latitude"
              type="text"
              placeholder="Ex: -3.8541"
              class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
            />
          </div>

          <!-- Longitude -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
              Longitude (Sede)
            </label>
            <input
              v-model="form.longitude"
              type="text"
              placeholder="Ex: -52.5012"
              class="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all"
            />
          </div>
        </div>

        <!-- Alerta de Validação -->
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
            {{ isEditMode ? 'Salvar Alterações' : 'Cadastrar Propriedade' }}
          </BaseButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { db, type Propriedade, type Produtor, offlineSave, gerarIdLocal } from '~/utils/db'

const route = useRoute()
const paramId = route.params.id as string

const isEditMode = computed(() => paramId !== 'novo')

const form = ref<Partial<Propriedade>>({
  nome: '',
  id_produtor: '',
  municipio: '',
  car_numero: '',
  codigo_incra: '',
  area_total: undefined,
  latitude: '',
  longitude: ''
})

const producers = ref<Produtor[]>([])
const saving = ref(false)
const validationError = ref<string | null>(null)

// Carrega os produtores agropecuários da base local (Dexie)
const loadProducers = async () => {
  if (process.client && db) {
    try {
      producers.value = await db.produtores.toArray()
    } catch (err) {
      console.error('[Propriedades] Erro ao buscar produtores locais:', err)
    }
  }
}

// Carrega dados da propriedade para edição
const loadProperty = async () => {
  if (isEditMode.value && process.client && db) {
    try {
      const data = await db.propriedades.get(paramId)
      if (data) {
        // Suporta tanto id_produtor quanto produtor_id do legado
        const prodId = data.id_produtor || data.produtor_id
        form.value = { 
          ...data,
          id_produtor: prodId ? String(prodId) : ''
        }
      } else {
        validationError.value = 'Propriedade não encontrada na base local.'
      }
    } catch (err) {
      console.error('[Propriedades] Erro ao buscar propriedade:', err)
      validationError.value = 'Erro ao carregar dados do registro.'
    }
  }
}

onMounted(async () => {
  await loadProducers()
  await loadProperty()
})

const goBack = () => {
  navigateTo('/cadastro/propriedades')
}

// Gravação e Validação Offline de Propriedades
const submitForm = async () => {
  validationError.value = null

  if (!form.value.nome || form.value.nome.trim().length < 3) {
    validationError.value = 'O nome da propriedade deve conter pelo menos 3 caracteres.'
    return
  }

  if (!form.value.id_produtor) {
    validationError.value = 'A vinculação com um produtor agropecuário é obrigatória.'
    return
  }

  if (!form.value.municipio || form.value.municipio.trim().length === 0) {
    validationError.value = 'O município da propriedade é obrigatório.'
    return
  }

  saving.value = true

  try {
    const finalData = { 
      ...form.value,
      // Salva de forma consistente em ambos os formatos legados
      produtor_id: form.value.id_produtor,
      id_produtor: form.value.id_produtor
    }

    if (!isEditMode.value) {
      finalData.id = gerarIdLocal()
    }

    // Persiste localmente e enfileira para sincronia posterior
    await offlineSave('propriedades', finalData as Record<string, unknown>)

    // Sucesso, retorna à listagem
    goBack()
  } catch (err) {
    console.error('[Propriedades] Falha ao gravar no IndexedDB:', err)
    validationError.value = 'Erro ao salvar registro de propriedade na base local.'
  } finally {
    saving.value = false
  }
}
</script>
