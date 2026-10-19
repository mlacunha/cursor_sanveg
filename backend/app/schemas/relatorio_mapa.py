from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional, Union
from decimal import Decimal, InvalidOperation
from datetime import datetime
import logging

# Nested location schemas
from app.schemas.municipio import MunicipioResponse
from app.schemas.estado import EstadoResponse

logger = logging.getLogger(__name__)


# Função auxiliar para normalizar coordenadas
def normalize_coordinate_value(v):
    """
    Converte e valida coordenadas geográficas com robustez total.
    
    Aceita:
    - Formato brasileiro: -48,1234 (vírgula como separador decimal)
    - Formato internacional: -48.1234 (ponto como separador decimal)
    - String ou número
    - Valores vazios (retorna None)
    
    Validações:
    - Remove espaços extras
    - Converte vírgula para ponto
    - Valida range (-180 a 180)
    - Retorna None para valores inválidos
    """
    if v is None or v == '' or v == '-':
        return None
    
    if isinstance(v, str):
        # Remove espaços e converte vírgula para ponto (BR → Internacional)
        v = v.strip().replace(',', '.')
        if not v or v == '-':
            return None
    
    try:
        result = Decimal(str(v))
        # Validar range de coordenadas geográficas
        if abs(result) > 180:
            return None  # Coordenada fora do range válido
        return result
    except (InvalidOperation, ValueError):
        return None  # Não conseguiu converter


# Schemas Inline para relacionamentos


class ProgramaInlineRelatorio(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    nome: str


class OrgaoInlineRelatorio(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    nome: str


class UserInlineRelatorio(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    login: str
    nome: Optional[str] = None
    email: Optional[str] = None


class PropriedadeInlineRelatorio(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    nome: str
    municipio: str
    UF: str


# Schemas principais


class RelatorioMapaCreate(BaseModel):
    """Schema para criação - `id`/`ano`/`trimestre` gerados pelo banco.
    Apenas `id_programa` e `data` são obrigatórios; os demais são
    opcionais conforme solicitado.
    """
    id_programa: str = Field(..., description="ID do programa (obrigatório)")
    data: str = Field(..., description="Data de referência (obrigatória)")
    orgao: Optional[str] = Field(None, description="ID do órgão (opcional)")
    id_usuario: Optional[str] = Field(
        None,
        description="Login do usuário (opcional)"
    )
    termo_inspecao: Optional[int] = Field(
        None,
        description="Número do termo de inspeção (opcional)"
    )
    termo_coleta: Optional[int] = Field(
        None,
        description="Número do termo de coleta (opcional)"
    )
    id_propriedade: Optional[str] = Field(
        None,
        description="ID da propriedade (opcional)"
    )
    tipo_imovel: Optional[str] = Field(None, description="Tipo do imóvel")
    municipio: Optional[str] = Field(None, description="Município")
    cultura: Optional[str] = Field(None, description="Cultura produzida")
    status: Optional[str] = Field(None, description="Status do relatório")
    latitude: Optional[Union[Decimal, str]] = Field(
        None,
        description="Latitude (aceita vírgula ou ponto)"
    )
    longitude: Optional[Union[Decimal, str]] = Field(
        None,
        description="Longitude (aceita vírgula ou ponto)"
    )

    @field_validator('latitude', 'longitude', mode='before')
    @classmethod
    def normalize_coordinate(cls, v):
        """Converte coordenada com vírgula para ponto e valida range"""
        return normalize_coordinate_value(v)

    @field_validator('id_propriedade', 'id_usuario', 'orgao', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        """Converte string vazia ou '-' em None"""
        if v == '' or v == '-' or v in ('null', 'NULL', 'None'):
            return None
        return v


class RelatorioMapaUpdate(BaseModel):
    """Schema para atualização - todos os campos opcionais (PATCH)"""
    data: Optional[str] = None
    orgao: Optional[str] = None
    id_usuario: Optional[str] = None
    termo_inspecao: Optional[int] = None
    termo_coleta: Optional[int] = None
    id_propriedade: Optional[str] = None
    tipo_imovel: Optional[str] = None
    municipio: Optional[str] = None
    cultura: Optional[str] = None
    status: Optional[str] = None
    latitude: Optional[Union[Decimal, str]] = None
    longitude: Optional[Union[Decimal, str]] = None

    @field_validator('latitude', 'longitude', mode='before')
    @classmethod
    def normalize_coordinate(cls, v):
        """Converte coordenada com vírgula para ponto e valida range"""
        return normalize_coordinate_value(v)

    @field_validator('id_propriedade', 'id_usuario', 'orgao', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        """Converte string vazia ou '-' em None"""
        if v == '' or v == '-' or v in ('null', 'NULL', 'None'):
            return None
        return v


class RelatorioMapaResponse(BaseModel):
    """Schema completo para resposta de um item."""
    id: int
    id_programa: str
    ano: Optional[str] = None
    data: str
    trimestre: Optional[int] = None
    orgao: Optional[str] = None
    id_usuario: Optional[str] = None
    termo_inspecao: Optional[int] = None
    termo_coleta: Optional[int] = None
    id_propriedade: Optional[str] = None
    tipo_imovel: Optional[str] = None
    municipio: Optional[str] = None
    cultura: Optional[str] = None
    status: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    coordenada: Optional[str] = None  # POINT convertido para texto

    # Nested location info
    municipio_info: Optional[MunicipioResponse] = None
    uf_info: Optional[EstadoResponse] = None

    # Relacionamentos opcionais
    programa_data: Optional[ProgramaInlineRelatorio] = None
    orgao_data: Optional[OrgaoInlineRelatorio] = None
    usuario_data: Optional[UserInlineRelatorio] = None
    propriedade_data: Optional[PropriedadeInlineRelatorio] = None

    model_config = ConfigDict(from_attributes=True)


class RelatorioMapaListResponse(BaseModel):
    """Schema usado pela listagem (sem o campo `coordenada`)."""
    id: int
    id_programa: str
    ano: Optional[str] = None
    data: str
    trimestre: Optional[int] = None
    orgao: Optional[str] = None
    id_usuario: Optional[str] = None
    termo_inspecao: Optional[int] = None
    termo_coleta: Optional[int] = None
    id_propriedade: Optional[str] = None
    tipo_imovel: Optional[str] = None
    municipio: Optional[str] = None
    cultura: Optional[str] = None
    status: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    # Nested location info
    municipio_info: Optional[MunicipioResponse] = None
    uf_info: Optional[EstadoResponse] = None

    # Relacionamentos opcionais
    programa_data: Optional[ProgramaInlineRelatorio] = None
    orgao_data: Optional[OrgaoInlineRelatorio] = None
    usuario_data: Optional[UserInlineRelatorio] = None
    propriedade_data: Optional[PropriedadeInlineRelatorio] = None

    model_config = ConfigDict(from_attributes=True)


class RelatorioMapaCSVRow(BaseModel):
    """Schema para validação de linha CSV"""
    id_programa: str
    data: str
    orgao: Optional[str] = None
    id_usuario: Optional[str] = None
    termo_inspecao: int
    termo_coleta: int
    id_propriedade: Optional[str] = None
    tipo_imovel: str
    municipio: str
    cultura: str
    status: str
    latitude: Optional[Union[Decimal, str]] = None
    longitude: Optional[Union[Decimal, str]] = None

    @model_validator(mode='before')
    @classmethod
    def corrigir_municipio_quebrado(cls, values):
        """
        Valida e corrige nomes de municípios quebrados usando API do IBGE.
        
        Se municipio + início da cultura formam um nome válido do IBGE,
        corrige automaticamente ambos os campos.
        
        Exemplo: municipio='Nova', cultura='Esperança do Piriá Laranja'
                 → municipio='NOVA ESPERANÇA DO PIRIÁ', cultura='LARANJA'
        """
        from app.utils.ibge_municipios import encontrar_municipio_correto
        
        municipio = values.get('municipio', '')
        cultura = values.get('cultura', '')
        
        if not municipio or not cultura:
            return values
        
        # Tentar encontrar o município correto
        municipio_corrigido, cultura_corrigida = (
            encontrar_municipio_correto(municipio, cultura)
        )
        
        # Se encontrou correção, aplicar
        if municipio_corrigido and cultura_corrigida:
            logger.info(
                f"CSV: Município corrigido de '{municipio}' + "
                f"'{cultura}' para '{municipio_corrigido}' + "
                f"'{cultura_corrigida}'"
            )
            values['municipio'] = municipio_corrigido
            values['cultura'] = cultura_corrigida
        
        return values

    @field_validator('data', mode='before')
    @classmethod
    def convert_date_format(cls, v):
        """Converte data do formato DD/MM/YYYY para YYYY-MM-DD"""
        if not v or v.strip() == '':
            raise ValueError("Data é obrigatória")
        
        # Remove espaços extras
        v = v.strip()
        
        # Tenta converter de DD/MM/YYYY para YYYY-MM-DD
        try:
            # Parse no formato brasileiro
            date_obj = datetime.strptime(v, '%d/%m/%Y')
            # Retorna no formato ISO
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            # Se já estiver no formato ISO, retorna como está
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError(
                    f"Data deve estar no formato DD/MM/YYYY ou "
                    f"YYYY-MM-DD, recebido: {v}"
                )

    @field_validator('latitude', 'longitude', mode='before')
    @classmethod
    def normalize_coordinate(cls, v):
        """Converte coordenada com vírgula para ponto e valida range"""
        return normalize_coordinate_value(v)

    @field_validator('id_propriedade', 'id_usuario', 'orgao', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        """Converte string vazia ou '-' em None"""
        if v == '' or v == '-' or v in ('null', 'NULL', 'None'):
            return None
        return v
    
    @field_validator('termo_inspecao', 'termo_coleta', mode='before')
    @classmethod
    def empty_string_to_zero(cls, v):
        """Converte string vazia em 0 para campos inteiros obrigatórios"""
        if v == '' or v == '-' or v in ('null', 'NULL', 'None'):
            return 0
        return v


class RelatorioMapaMunicipalMensal(BaseModel):
    """Schema para agregacao mensal por municipio"""
    id_programa: str
    municipio: str
    
    programa_data: Optional[ProgramaInlineRelatorio] = None
    
    N1: int = 0
    N2: int = 0
    N3: int = 0
    N4: int = 0
    N5: int = 0
    N6: int = 0
    N7: int = 0
    N8: int = 0
    N9: int = 0
    N10: int = 0
    N11: int = 0
    N12: int = 0
    NT: int = 0
    
    S1: int = 0
    S2: int = 0
    S3: int = 0
    S4: int = 0
    S5: int = 0
    S6: int = 0
    S7: int = 0
    S8: int = 0
    S9: int = 0
    S10: int = 0
    S11: int = 0
    S12: int = 0
    ST: int = 0
    
    P1: int = 0
    P2: int = 0
    P3: int = 0
    P4: int = 0
    P5: int = 0
    P6: int = 0
    P7: int = 0
    P8: int = 0
    P9: int = 0
    P10: int = 0
    P11: int = 0
    P12: int = 0
    PT: int = 0

    # Nested location info (best-effort match by name)
    municipio_info: Optional[MunicipioResponse] = None
    uf_info: Optional[EstadoResponse] = None

    model_config = ConfigDict(from_attributes=True)
