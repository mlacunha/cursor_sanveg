<template>
  <header class="sticky top-0 z-30 bg-white/95 dark:bg-slate-900/95 backdrop-blur-sm border-b border-gray-100 dark:border-gray-800 px-6 py-4 flex items-center justify-between shadow-sm">
    <!-- Left: Title and Subtitle -->
    <div class="flex items-center gap-4">
      <BaseButton 
        variant="ghost" 
        size="icon"
        icon="lucide:arrow-left"
        title="Voltar"
        class="text-slate-400 hover:text-slate-600"
        @click="$emit('back')"
      />
      <div>
        <h1 class="text-lg font-bold text-gray-900 dark:text-white leading-tight">
          {{ title }}
        </h1>
        <p v-if="subtitle" class="text-xs text-gray-500 font-medium">
          {{ subtitle }}
        </p>
      </div>
    </div>

    <!-- Right: Actions -->
    <div class="flex items-center gap-3">
      <BaseButton 
        variant="outline"
        @click="$emit('back')"
      >
        Cancelar
      </BaseButton>
      
      <BaseButton 
        variant="primary"
        :loading="loading"
        icon="lucide:save"
        @click="$emit('save')"
      >
        Salvar
      </BaseButton>
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
  loading?: boolean
}>()

defineEmits(['back', 'save'])
</script>
