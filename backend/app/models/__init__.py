# Importar todos os modelos para garantir que estejam registrados no Base (metadata)
# antes de Base.metadata.create_all() ser chamado.
# A ORDEM IMPORTA: tabelas referenciadas por FKs devem vir antes das que as referenciam.

from app.models.estado import Estado
from app.models.municipio import Municipio
from app.models.orgao_tipo import OrgaoTipo
from app.models.orgao import Orgao
from app.models.unidade import Unidade
from app.models.cargo import Cargo
from app.models.formacao import Formacao
from app.models.users import User
from app.models.programa import Programa
from app.models.hospedeiro import Hospedeiro
from app.models.norma import Norma
from app.models.produtor import Produtor
from app.models.propriedade import Propriedade
from app.models.termo_inspecao import TermoInspecao
from app.models.area_inspecionada import AreaInspecionada
from app.models.area_programa import AreaPrograma
from app.models.amostra_coletada import AmostraColetada
from app.models.inspecao_foto import InspecaoFoto
from app.models.relatorio_mapa import RelatorioMapa
from app.models.controle_sequencial import ControleSequencial
from app.models.laboratorio import Laboratorio
from app.models.mapa_view import MapaLevantamento
from app.models.car_propriedade import CarPropriedade

__all__ = [
    "Estado",
    "Municipio",
    "OrgaoTipo",
    "Orgao",
    "Unidade",
    "Cargo",
    "Formacao",
    "User",
    "Programa",
    "Hospedeiro",
    "Norma",
    "Produtor",
    "Propriedade",
    "TermoInspecao",
    "AreaInspecionada",
    "AreaPrograma",
    "AmostraColetada",
    "InspecaoFoto",
    "RelatorioMapa",
    "ControleSequencial",
    "Laboratorio",
    "MapaLevantamento",
    "CarPropriedade",
]
