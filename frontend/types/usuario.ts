export interface Usuario {
  id: string | number
  nome: string
  email: string
  cpf: string
  telefone: string
  matricula: string
  carteira_fiscal: string
  senha?: string
  ativo: boolean
  perfil_acesso: 'ADMIN' | 'TECNICO' | 'EXTERNO'
  orgao_vinculado: string
  unidade_lotacao: string
  cargo: string
  formacao: string
  created_at?: string
  updated_at?: string
}
