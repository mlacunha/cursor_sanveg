<script setup lang="ts">
const { usuarios, loading } = useUsuarios()

const columns = [
  { key: 'nome', label: 'Nome e Login' },
  { key: 'perfil_acesso', label: 'Permissão (Perfil)' },
  { key: 'orgao_vinculado', label: 'Instituição (Órgão)' },
  { key: 'formacao', label: 'Formação Acadêmica' },
  { key: 'matricula', label: 'Matrícula / CF' }
]

const handleAdd = () => {
  navigateTo('/usuarios/novo')
}

const handleEdit = (user: any) => {
  navigateTo(`/usuarios/${user.id}`)
}

const handleDelete = (user: any) => {
  // TODO: Implement delete logic with confirmation
  console.log('Delete user', user)
}
</script>

<template>
  <div class="p-6">
    <BaseDataTable
      title="Usuários"
      subtitle="Controle de acesso e permissões (RBAC)"
      :columns="columns"
      :items="usuarios"
      :loading="loading"
      search-placeholder="Buscar por Nome, Email ou CPF..."
      show-add-button
      add-label="Novo Usuário"
      show-row-actions
      @add="handleAdd"
      @edit="handleEdit"
      @delete="handleDelete"
    >
      <!-- Custom slots for table columns -->
      <template #col-nome="{ item }">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-full bg-brand-blue/10 flex items-center justify-center text-brand-blue">
            <Icon name="lucide:user" size="18" />
          </div>
          <div>
            <div class="font-bold text-slate-800 leading-tight">{{ item.nome }}</div>
            <div class="text-xs text-slate-500">{{ item.email }}</div>
          </div>
        </div>
      </template>

      <template #col-perfil_acesso="{ value }">
        <span 
          class="px-2.5 py-1 rounded-md text-[10px] font-extrabold uppercase tracking-wider shadow-sm"
          :class="{
            'bg-brand-blue/10 text-brand-blue border border-brand-blue/20': value === 'ADMIN',
            'bg-slate-100 text-slate-600 border border-slate-200': value !== 'ADMIN'
          }"
        >
          {{ value }}
        </span>
      </template>

      <template #col-orgao_vinculado="{ value }">
        <div class="flex items-center gap-2 max-w-[280px]">
          <Icon name="lucide:building-2" size="14" class="text-slate-400 shrink-0" />
          <span class="truncate text-xs font-medium text-slate-600">{{ value }}</span>
        </div>
      </template>

      <template #col-formacao="{ value }">
        <span class="text-xs text-slate-600">{{ value }}</span>
      </template>

      <template #col-matricula="{ item }">
        <div class="text-[10px] leading-tight flex flex-col gap-0.5">
          <div class="text-slate-400 uppercase font-bold tracking-tight">Mat: <span class="text-slate-600">{{ item.matricula }}</span></div>
          <div class="text-slate-400 uppercase font-bold tracking-tight">CF: <span class="text-slate-600">{{ item.carteira_fiscal }}</span></div>
        </div>
      </template>
    </BaseDataTable>
  </div>
</template>
