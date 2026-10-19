<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
        <Transition
          enter-active-class="transition duration-300 ease-out"
          enter-from-class="opacity-0 scale-95 translate-y-4"
          enter-to-class="opacity-100 scale-100 translate-y-0"
          leave-active-class="transition duration-200 ease-in"
          leave-from-class="opacity-100 scale-100 translate-y-0"
          leave-to-class="opacity-0 scale-95 translate-y-4"
        >
          <div
            v-if="show"
            class="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden border border-gray-100 dark:border-gray-800"
            @click.stop
          >
            <!-- Header -->
            <div class="px-8 py-6 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between bg-gray-50/50 dark:bg-gray-800/50">
              <h3 class="text-xl font-bold text-gray-800 dark:text-white">{{ title }}</h3>
              <BaseButton
                variant="ghost"
                size="icon"
                icon="lucide:x"
                class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                @click="$emit('close')"
              />
            </div>

            <!-- Body -->
            <div class="px-8 py-6">
              <slot></slot>
            </div>

            <!-- Footer -->
            <div class="px-8 py-6 border-t border-gray-100 dark:border-gray-800 flex items-center justify-end gap-3 bg-gray-50/50 dark:bg-gray-800/50">
              <BaseButton
                variant="outline"
                :disabled="loading"
                @click="$emit('close')"
              >
                Cancelar
              </BaseButton>
              <BaseButton
                variant="primary"
                :loading="loading"
                @click="$emit('confirm')"
              >
                {{ confirmLabel || 'Confirmar' }}
              </BaseButton>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
defineProps<{
  show: boolean
  title: string
  confirmLabel?: string
  loading?: boolean
}>()

defineEmits(['close', 'confirm'])
</script>
