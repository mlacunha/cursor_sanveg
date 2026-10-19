import Dexie, { type Table } from 'dexie';

/**
 * Interfaces das tabelas do Dexie (IndexedDB) herdadas do legado.
 */
export interface DashboardCacheRow {
  id: string;
  data?: unknown;
  updatedAt?: string;
  [key: string]: unknown;
}

export interface Programa {
  id: string;
  nome?: string;
  codigo?: string;
  [key: string]: unknown;
}

export interface Hospedeiro {
  id: string;
  id_programa?: string;
  nomes_comuns?: string;
  nome_cientifico?: string;
  [key: string]: unknown;
}

export interface Norma {
  id: string;
  id_programa?: string;
  nome_norma?: string;
  [key: string]: unknown;
}

export interface Formacao {
  id: string;
  nome?: string;
  [key: string]: unknown;
}

export interface Propriedade {
  id: string;
  nome?: string;
  municipio?: string;
  [key: string]: unknown;
}

export interface Produtor {
  id: string;
  nome?: string;
  [key: string]: unknown;
}

export interface TipoOrgao {
  id: string;
  nome?: string;
  [key: string]: unknown;
}

export interface Orgao {
  id: string;
  id_tipo_orgao?: string;
  nome?: string;
  sigla?: string;
  [key: string]: unknown;
}

export interface Unidade {
  id: string;
  id_orgao?: string;
  nome?: string;
  municipio?: string;
  [key: string]: unknown;
}

export interface Cargo {
  id: string;
  id_orgao?: string;
  nome?: string;
  [key: string]: unknown;
}

export interface Usuario {
  id: string;
  nome?: string;
  email?: string;
  cpf?: string;
  telefone?: string;
  matricula?: string;
  carteirafiscal?: string;
  role?: string;
  id_orgao?: string;
  id_cargo?: string;
  id_unidade?: string;
  id_formacao?: string;
  [key: string]: unknown;
}

export interface TermoInspecao {
  id: string;
  id_propriedade?: string;
  id_programa?: string;
  data_inspecao?: string;
  termo_coleta?: string | number;
  [key: string]: unknown;
}

export interface AreaInspecionada {
  id: string;
  id_termo_inspecao?: string;
  nome_local?: string;
  latitude?: string;
  longitude?: string;
  obs?: string;
  [key: string]: unknown;
}

export interface AreaPrograma {
  id: string;
  id_area?: string;
  id_programa?: string;
  especie?: string | null;
  variedade?: string | null;
  material_multiplicacao?: string | null;
  origem?: string | null;
  idade_plantio?: string | null;
  area_plantada?: string | null;
  numero_plantas?: string | null;
  numero_inspecionadas?: string | null;
  numero_suspeitas?: string | null;
  resultado?: string | null;
  obs?: string | null;
  latitude?: string;
  longitude?: string;
  nome_local?: string;
  tipo_area?: string;
  [key: string]: unknown;
}

export interface AmostraColetada {
  id: string;
  id_area_programa?: string;
  parte_coletada?: string;
  latitude?: string;
  longitude?: string;
  raiz?: boolean;
  caule?: boolean;
  peciolo?: boolean;
  folha?: boolean;
  fruto?: boolean;
  flor?: boolean;
  semente?: boolean;
  data_envio_laboratorio?: string | null;
  id_laboratorio?: string | null;
  processo_sei?: string | null;
  data_resultado?: string | null;
  resultado_laboratorio?: string | null;
  laudo_arquivo?: string | null;
  [key: string]: unknown;
}

export interface Laboratorio {
  id: string;
  nome?: string;
  tipo?: string | null;
  cnpj?: string | null;
  endereco?: string | null;
  cep?: string | null;
  cidade?: string | null;
  uf?: string | null;
  contato?: string | null;
  instrumento_reconhecimento?: string | null;
  contato_nome?: string | null;
  contato_cargo?: string | null;
  contato_email?: string | null;
  contato_telefone?: string | null;
  [key: string]: unknown;
}

export interface SyncQueueItem {
  id?: number;
  action: string;
  route: string;
  payload: unknown;
  timestamp: number;
}

export type TableName =
  | 'dashboardCache'
  | 'programas'
  | 'hospedeiros'
  | 'normas'
  | 'formacoes'
  | 'propriedades'
  | 'produtores'
  | 'tipos_orgao'
  | 'orgaos'
  | 'unidades'
  | 'cargos'
  | 'usuarios'
  | 'laboratorios'
  | 'termo_inspecao'
  | 'area_inspecionada'
  | 'area_programa'
  | 'amostra_coletada'
  | 'syncQueue';

const storesV1 = {
  dashboardCache: 'id',
  programas: 'id, nome, codigo',
  propriedades: 'id, nome, municipio',
  produtores: 'id, nome',
  termo_inspecao: 'id, id_propriedade, id_programa, data_inspecao',
  area_inspecionada: 'id, id_termo_inspecao, nome_local',
  syncQueue: '++id, action, route, payload, timestamp',
};

const storesV2 = {
  ...storesV1,
  hospedeiros: 'id, id_programa, nomes_comuns, nome_cientifico',
  normas: 'id, id_programa, nome_norma',
  tipos_orgao: 'id, nome',
  orgaos: 'id, id_tipo_orgao, nome, sigla',
  unidades: 'id, id_orgao, nome, municipio',
  cargos: 'id, id_orgao, nome',
  usuarios: 'id, nome, email, cpf, telefone, role, id_orgao, id_cargo, id_unidade',
};

const storesV4 = {
  ...storesV2,
  usuarios: 'id, nome, email, cpf, telefone, matricula, carteirafiscal, role, id_orgao, id_cargo, id_unidade',
};

const storesV5 = {
  ...storesV4,
  formacoes: 'id, nome',
  usuarios: 'id, nome, email, cpf, telefone, matricula, carteirafiscal, role, id_orgao, id_cargo, id_unidade, id_formacao',
};

const storesV8 = {
  dashboardCache: 'id',
  programas: 'id, nome, codigo',
  hospedeiros: 'id, id_programa, nomes_comuns, nome_cientifico',
  normas: 'id, id_programa, nome_norma',
  formacoes: 'id, nome',
  propriedades: 'id, nome, municipio',
  produtores: 'id, nome',
  tipos_orgao: 'id, nome',
  orgaos: 'id, id_tipo_orgao, nome, sigla',
  unidades: 'id, id_orgao, nome, municipio',
  cargos: 'id, id_orgao, nome',
  usuarios: 'id, nome, email, cpf, telefone, matricula, carteirafiscal, role, id_orgao, id_cargo, id_unidade, id_formacao',
  termo_inspecao: 'id, id_propriedade, data_inspecao',
  area_inspecionada: 'id, id_termo_inspecao',
  area_programa: 'id, id_area, id_programa',
  amostra_coletada: 'id, id_area_programa',
  syncQueue: '++id, action, route, payload, timestamp',
};

const storesV10 = {
  ...storesV8,
  laboratorios: 'id, nome',
};

export class SanvegDB extends Dexie {
  dashboardCache!: Table<DashboardCacheRow>;
  programas!: Table<Programa>;
  hospedeiros!: Table<Hospedeiro>;
  normas!: Table<Norma>;
  formacoes!: Table<Formacao>;
  propriedades!: Table<Propriedade>;
  produtores!: Table<Produtor>;
  tipos_orgao!: Table<TipoOrgao>;
  orgaos!: Table<Orgao>;
  unidades!: Table<Unidade>;
  cargos!: Table<Cargo>;
  usuarios!: Table<Usuario>;
  laboratorios!: Table<Laboratorio>;
  termo_inspecao!: Table<TermoInspecao>;
  area_inspecionada!: Table<AreaInspecionada>;
  area_programa!: Table<AreaPrograma>;
  amostra_coletada!: Table<AmostraColetada>;
  syncQueue!: Table<SyncQueueItem>;

  constructor() {
    super('SanvegDB');
    this.version(1).stores(storesV1);
    this.version(2).stores(storesV2);
    this.version(3).stores(storesV2);
    this.version(4).stores(storesV4);
    this.version(5).stores(storesV5);
    this.version(6).stores(storesV5).upgrade(async (tx) => {
      const termos = await tx.table('termo_inspecao').toArray();
      for (const t of termos) {
        if (t.id && String(t.id).startsWith('177')) await tx.table('termo_inspecao').delete(t.id);
      }
      const areas = await tx.table('area_inspecionada').toArray();
      for (const a of areas) {
        if ((a.id && String(a.id).startsWith('177')) || (a.id_termo_inspecao && String(a.id_termo_inspecao).startsWith('177'))) {
          await tx.table('area_inspecionada').delete(a.id);
        }
      }
      await tx.table('syncQueue').clear();
    });
    this.version(7).stores(storesV5).upgrade(async (tx) => {
      const areas = await tx.table('area_inspecionada').toArray();
      for (const a of areas) {
        if ((a.id && String(a.id).startsWith('177')) || (a.id_termo_inspecao && String(a.id_termo_inspecao).startsWith('177'))) {
          await tx.table('area_inspecionada').delete(a.id);
        }
      }
      const termos = await tx.table('termo_inspecao').toArray();
      for (const t of termos) {
        if (t.id && String(t.id).startsWith('177')) await tx.table('termo_inspecao').delete(t.id);
      }
      const queues = await tx.table('syncQueue').toArray();
      for (const q of queues) {
        const payload = q.payload as { id?: unknown } | undefined;
        if (payload?.id && String(payload.id).startsWith('177') && q.id != null) await tx.table('syncQueue').delete(q.id);
      }
    });
    this.version(8).stores(storesV8).upgrade(async (tx) => {
      const areas = await tx.table('area_inspecionada').toArray();
      for (const a of areas) {
        const row = a as Record<string, unknown>;
        if (row.id_programa) {
          await tx.table('area_programa').add({
            id: String(Date.now() + Math.floor(Math.random() * 1000)),
            id_area: a.id,
            id_programa: row.id_programa,
            especie: row.especie ?? null,
            variedade: row.variedade ?? null,
            material_multiplicacao: row.material_multiplicacao ?? null,
            origem: row.origem ?? null,
            idade_plantio: row.idade_plantio ?? null,
            area_plantada: row.area_plantada ?? null,
            numero_plantas: row.numero_plantas ?? null,
            numero_inspecionadas: row.numero_inspecionadas ?? null,
            numero_suspeitas: row.numero_suspeitas ?? null,
            resultado: row.resultado ?? null,
            obs: null,
          });
        }
      }
      await tx.table('syncQueue').clear();
    });
    const isNumericId = (id: unknown) =>
      id !== null && id !== undefined && !isNaN(Number(id));
    this.version(9).stores(storesV8).upgrade(async (tx) => {
      const areas = await tx.table('area_inspecionada').toArray();
      for (const a of areas) {
        if (isNumericId(a.id)) await tx.table('area_inspecionada').delete(a.id);
      }
      const progs = await tx.table('area_programa').toArray();
      for (const p of progs) {
        if (isNumericId(p.id) || isNumericId(p.id_area)) await tx.table('area_programa').delete(p.id);
      }
      const amostras = await tx.table('amostra_coletada').toArray();
      for (const s of amostras) {
        if (isNumericId(s.id) || isNumericId(s.id_area_programa)) await tx.table('amostra_coletada').delete(s.id);
      }
      await tx.table('syncQueue').clear();
    });
    this.version(10).stores(storesV10);
  }
}

// Instanciação segura no lado do cliente
export const db = process.client ? new SanvegDB() : (null as unknown as SanvegDB);

/**
 * Helpers para gravação offline e enfileiramento na fila de sync.
 */
export async function offlineSave(tableName: TableName, data: Record<string, unknown>): Promise<void> {
  if (!process.client || !db) return;
  const table = (db as unknown as Record<string, { put: (d: Record<string, unknown>) => Promise<unknown> }>)[tableName];
  await table.put(data);
  await db.syncQueue.add({
    action: 'put',
    route: tableName,
    payload: data,
    timestamp: Date.now(),
  });
}

export async function offlineDelete(tableName: TableName, id: string | number): Promise<void> {
  if (!process.client || !db) return;
  const table = (db as unknown as Record<string, { delete: (id: string | number) => Promise<unknown> }>)[tableName];
  await table.delete(id);
  await db.syncQueue.add({
    action: 'delete',
    route: tableName,
    payload: { id },
    timestamp: Date.now(),
  });
}

/**
 * Gera um UUID local para registros offline compatível com VARCHAR(36) no banco de dados.
 */
export function gerarIdLocal(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback simples caso randomUUID não esteja disponível
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}
