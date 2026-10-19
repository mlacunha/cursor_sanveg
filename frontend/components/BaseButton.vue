<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="relative flex items-center justify-center gap-2 rounded-xl font-semibold transition-all duration-200 outline-none disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]"
    :class="[
      variantClasses[variant],
      sizeClasses[size],
      { 'w-full': block }
    ]"
    @click="$emit('click', $event)"
  >
    <!-- Loading Spinner -->
    <div 
      v-if="loading" 
      class="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin"
      :class="{ 'absolute': $slots.default && !icon }"
    ></div>
    
    <!-- Icon -->
    <Icon 
      v-if="icon && !loading" 
      :name="icon" 
      :class="iconSizeClasses[size]" 
    />
    
    <!-- Content Slot -->
    <span v-if="$slots.default" :class="{ 'opacity-0': loading && icon }">
      <slot />
    </span>
  </button>
</template>

<script setup lang="ts">
/**
 * Protocolo SVEGPA: BaseButton
 * Este componente é a ÚNICA forma permitida de renderizar botões no sistema.
 */

type Variant = 'primary' | 'outline' | 'danger' | 'ghost'
type Size = 'sm' | 'md' | 'lg' | 'icon'

const props = withDefaults(defineProps<{
  variant?: Variant
  size?: Size
  icon?: string
  loading?: boolean
  disabled?: boolean
  block?: boolean
  type?: 'button' | 'submit'
}>(), {
  variant: 'primary',
  size: 'md',
  loading: false,
  disabled: false,
  block: false,
  type: 'button'
})

defineEmits(['click'])

const variantClasses: Record<Variant, string> = {
  // Protocolo Rule 14: bg-[#1714EF] text-white
  primary: 'bg-[#1714EF] text-white hover:opacity-90 shadow-lg shadow-[#1714EF]/20 focus:ring-2 focus:ring-[#1714EF]/20',
  
  // Protocolo Rule 15: border border-slate-300 text-slate-700 bg-white
  outline: 'border border-slate-300 text-slate-700 bg-white hover:bg-slate-50 hover:border-slate-400 focus:ring-2 focus:ring-slate-100',
  
  // Protocolo Rule 16: bg-red-600 text-white
  danger: 'bg-red-600 text-white hover:bg-red-700 shadow-lg shadow-red-500/20 focus:ring-2 focus:ring-red-500/20',
  
  // Utilizado para ícones e botões de navegação sutis (Protocolo Rule 17)
  ghost: 'bg-transparent hover:bg-slate-100 dark:hover:bg-slate-800'
}

const sizeClasses: Record<Size, string> = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-6 py-2.5 text-sm',
  lg: 'px-8 py-3.5 text-base',
  icon: 'p-2' // Para botões de ação em tabelas
}

const iconSizeClasses: Record<Size, string> = {
  sm: 'w-3.5 h-3.5',
  md: 'w-4 h-4',
  lg: 'w-5 h-5',
  icon: 'w-4 h-4'
}
</script>
