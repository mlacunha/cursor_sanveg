import type { Usuario } from '~/types/usuario'

export const useUsuarios = () => {
  const usuarios = useState<Usuario[]>('usuarios_list', () => [
    {
      id: 1,
      nome: 'MILTON LEITE ALVES DA CUNHA',
      email: 'milton.cunha@agro.gov.br',
      cpf: '123.123.123-13',
      telefone: '91 98813-8748',
      matricula: '1321321',
      carteira_fiscal: 'CF 2624654',
      ativo: true,
      perfil_acesso: 'ADMIN',
      orgao_vinculado: 'MAPA - Ministério da Agricultura e Pecuária',
      unidade_lotacao: 'Serviço de Fiscalização, Inspeção e Sanidade Vegetal - SISV/DDA/SFA-PA (Belém - PA)',
      cargo: 'Auditor Fiscal Federal Agropecuário - AFFA',
      formacao: 'Engenheiro(a) Agrônomo(a)'
    }
  ])

  const loading = ref(false)
  const error = ref<string | null>(null)

  const getUsuarioById = (id: string | number) => {
    return usuarios.value.find(u => String(u.id) === String(id))
  }

  const addUsuario = (usuario: Omit<Usuario, 'id'>) => {
    const newId = usuarios.value.length + 1
    usuarios.value.push({ ...usuario, id: newId })
  }

  const updateUsuario = (id: string | number, updatedData: Partial<Usuario>) => {
    const index = usuarios.value.findIndex(u => String(u.id) === String(id))
    if (index !== -1) {
      usuarios.value[index] = { ...usuarios.value[index], ...updatedData }
    }
  }

  const deleteUsuario = (id: string | number) => {
    usuarios.value = usuarios.value.filter(u => String(u.id) !== String(id))
  }

  return {
    usuarios,
    loading,
    error,
    getUsuarioById,
    addUsuario,
    updateUsuario,
    deleteUsuario
  }
}
