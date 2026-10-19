<template>
  <div class="border-b border-gray-100 dark:border-gray-800 bg-white dark:bg-slate-900">
    <nav class="flex space-x-8 px-6" aria-label="Tabs">
      <BaseButton
        v-for="tab in tabs"
        :key="tab.value"
        variant="ghost"
        class="!py-4 !px-1 border-b-2 !font-medium !text-sm !rounded-none transition-all relative whitespace-nowrap"
        :class="[
          modelValue === tab.value
            ? '!border-[#1714EF] !text-[#1714EF]'
            : '!border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
        ]"
        @click="$emit('update:modelValue', tab.value)"
      >
        <div class="flex items-center gap-2">
          <Icon v-if="tab.icon" :name="tab.icon" class="w-4 h-4" />
          {{ tab.label }}
        </div>
      </BaseButton>
    </nav>
  </div>
</template>

<script setup lang="ts">
interface Tab {
  label: string
  value: string
  icon?: string
}

defineProps<{
  tabs: Tab[]
  modelValue: string
}>()

defineEmits(['update:modelValue'])
</script>
