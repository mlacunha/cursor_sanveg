"""
Módulo para carregar e cachear a lista oficial de municípios do IBGE.

Fornece funcionalidade de Longest Prefix Match para corrigir nomes de municípios
quebrados incorretamente em arquivos CSV.
"""
import requests
import logging
from typing import Dict, Optional, Tuple
from functools import lru_cache

logger = logging.getLogger(__name__)

# URL oficial da API do IBGE para municípios do Pará
IBGE_API_URL = (
    "https://servicodados.ibge.gov.br/api/v1/localidades/"
    "estados/PA/municipios"
)

# Cache global: chave=UPPERCASE (matching), valor=grafia original IBGE
_MUNICIPIOS_CACHE: Optional[Dict[str, str]] = None


def carregar_municipios_ibge(force_reload: bool = False) -> Dict[str, str]:
    """
    Carrega municípios do IBGE como dicionário.
    
    Args:
        force_reload: Se True, força recarregamento da API
        
    Returns:
        Dict[str, str]: {"NOME UPPERCASE": "Nome Original IBGE"}
        
    Raises:
        Exception: Se falhar ao carregar da API do IBGE
    """
    global _MUNICIPIOS_CACHE
    
    # Retornar do cache se já existe e não é force reload
    if _MUNICIPIOS_CACHE is not None and not force_reload:
        logger.debug(
            f"Retornando {len(_MUNICIPIOS_CACHE)} municípios do cache"
        )
        return _MUNICIPIOS_CACHE
    
    try:
        logger.info("Carregando lista de municípios do IBGE...")
        response = requests.get(IBGE_API_URL, timeout=10)
        response.raise_for_status()
        
        municipios_data = response.json()
        
        # Dicionário: chave=UPPERCASE (match), valor=original (save)
        municipios = {
            municipio['nome'].upper().strip(): municipio['nome'].strip()
            for municipio in municipios_data
        }
        
        _MUNICIPIOS_CACHE = municipios
        logger.info(
            f"Carregados {len(municipios)} municípios do IBGE com sucesso"
        )
        
        return municipios
        
    except Exception as e:
        logger.error(f"Erro ao carregar municípios do IBGE: {e}")
        
        # Se falhar e não temos cache, usar lista fallback mínima
        if _MUNICIPIOS_CACHE is None:
            logger.warning("Usando lista fallback de municípios")
            _MUNICIPIOS_CACHE = _get_fallback_municipios()
            
        return _MUNICIPIOS_CACHE


def _get_fallback_municipios() -> Dict[str, str]:
    """
    Lista fallback de municípios do Pará.
    Retorna dict com chave=UPPERCASE e valor=Title Case.
    """
    municipios_lista = [
        "Abaetetuba", "Abel Figueiredo", "Acará", "Afuá",
        "Água Azul do Norte", "Alenquer", "Almeirim", "Altamira",
        "Anajás", "Ananindeua", "Anapu", "Augusto Corrêa",
        "Aurora do Pará", "Aveiro", "Bagre", "Baião", "Bannach",
        "Barcarena", "Belém", "Belterra", "Benevides",
        "Bom Jesus do Tocantins", "Bonito", "Bragança", "Brasil Novo",
        "Brejo Grande do Araguaia", "Breu Branco", "Breves", "Bujaru",
        "Cachoeira do Arari", "Cachoeira do Piriá", "Cametá",
        "Canaã dos Carajás", "Capanema", "Capitão Poço", "Castanhal",
        "Chaves", "Colares", "Conceição do Araguaia",
        "Concórdia do Pará", "Cumaru do Norte", "Curionópolis",
        "Curralinho", "Curuá", "Curuçá", "Dom Eliseu",
        "Eldorado dos Carajás", "Faro", "Floresta do Araguaia",
        "Garrafão do Norte", "Goianésia do Pará", "Gurupá",
        "Igarapé-Açu", "Igarapé-Miri", "Inhangapi", "Ipixuna do Pará",
        "Irituia", "Itaituba", "Itupiranga", "Jacareacanga",
        "Jacundá", "Juruti", "Limoeiro do Ajuru", "Mãe do Rio",
        "Magalhães Barata", "Marabá", "Maracanã", "Marapanim",
        "Marituba", "Medicilândia", "Melgaço", "Mocajuba", "Moju",
        "Monte Alegre", "Muaná", "Nova Esperança do Piriá",
        "Nova Ipixuna", "Nova Timboteua", "Novo Progresso",
        "Novo Repartimento", "Óbidos", "Oeiras do Pará",
        "Oriximiná", "Ourém", "Ourilândia do Norte", "Pacajá",
        "Palestina do Pará", "Paragominas", "Parauapebas",
        "Pau D'Arco", "Peixe-Boi", "Piçarra", "Placas",
        "Ponta de Pedras", "Portel", "Porto de Moz", "Prainha",
        "Primavera", "Quatipuru", "Redenção", "Rio Maria",
        "Rondon do Pará", "Rurópolis", "Salinópolis", "Salvaterra",
        "Santa Bárbara do Pará", "Santa Cruz do Arari",
        "Santa Izabel do Pará", "Santa Luzia do Pará",
        "Santa Maria das Barreiras", "Santa Maria do Pará",
        "Santana do Araguaia", "Santarém", "Santarém Novo",
        "Santo Antônio do Tauá", "São Caetano de Odivelas",
        "São Domingos do Araguaia", "São Domingos do Capim",
        "São Félix do Xingu", "São Francisco do Pará",
        "São Geraldo do Araguaia", "São João da Ponta",
        "São João de Pirabas", "São João do Araguaia",
        "São Miguel do Guamá", "São Sebastião da Boa Vista",
        "Sapucaia", "Senador José Porfírio", "Soure", "Tailândia",
        "Terra Alta", "Terra Santa", "Tomé-Açu", "Tracuateua",
        "Trairão", "Tucumã", "Tucuruí", "Ulianópolis", "Uruará",
        "Vigia", "Viseu", "Vitória do Xingu", "Xinguara"
    ]
    
    # Converter lista para dicionário {UPPERCASE: Title Case}
    return {nome.upper(): nome for nome in municipios_lista}


def encontrar_municipio_correto(
    municipio_parcial: str,
    cultura_com_excesso: str,
    municipios: Optional[Dict[str, str]] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Implementa Longest Prefix Match para encontrar município correto.
    
    Verifica se municipio_parcial + início da cultura_com_excesso
    forma um nome válido do IBGE.
    
    Args:
        municipio_parcial: Nome parcial (ex: "Nova")
        cultura_com_excesso: Cultura com excesso
                            (ex: "Esperança do Piriá Laranja...")
        municipios: Dict de municípios (usa cache se None)
        
    Returns:
        Tupla (municipio_correto, cultura_corrigida) ou (None, None)
        
    Exemplo:
        >>> encontrar_municipio_correto(
        ...     "Nova", "Esperança do Piriá Laranja"
        ... )
        ("Nova Esperança do Piriá", "Laranja")
    """
    if municipios is None:
        municipios = carregar_municipios_ibge()
    
    # Normalizar inputs para matching
    municipio_upper = municipio_parcial.upper().strip()
    cultura_upper = cultura_com_excesso.upper().strip()
    
    # Se o município já está correto, não fazer nada
    if municipio_upper in municipios:
        return None, None
    
    # Dividir a cultura em palavras
    cultura_palavras = cultura_upper.split()
    
    if not cultura_palavras:
        return None, None
    
    # Testar concatenações progressivas (longest prefix match)
    # Começar com mais palavras e ir reduzindo
    melhor_match_key = None
    melhor_cultura_corrigida = None
    max_palavras_matched = 0
    
    for num_palavras in range(len(cultura_palavras), 0, -1):
        # Pegar N primeiras palavras da cultura
        palavras_teste = cultura_palavras[:num_palavras]
        
        # Concatenar município + palavras da cultura (UPPERCASE p/ match)
        candidato_key = municipio_upper + " " + " ".join(palavras_teste)
        
        # Verificar se existe nos municípios do IBGE
        if candidato_key in municipios:
            # Remover as palavras usadas da cultura
            cultura_restante = " ".join(cultura_palavras[num_palavras:])
            
            # Guardar o melhor match (mais palavras)
            if num_palavras > max_palavras_matched:
                melhor_match_key = candidato_key
                melhor_cultura_corrigida = cultura_restante
                max_palavras_matched = num_palavras
    
    if melhor_match_key:
        # Pegar o nome original (grafia IBGE) usando a chave
        municipio_original = municipios[melhor_match_key]
        
        # Capitalizar a cultura também (Title Case)
        cultura_corrigida = melhor_cultura_corrigida.title()
        
        logger.info(
            f"Correção aplicada: '{municipio_parcial}' + "
            f"'{cultura_com_excesso}' → "
            f"município='{municipio_original}', "
            f"cultura='{cultura_corrigida}'"
        )
        return municipio_original, cultura_corrigida
    
    # Não encontrou match
    return None, None


@lru_cache(maxsize=1)
def get_municipios_cache() -> Dict[str, str]:
    """
    Wrapper com cache LRU.
    
    Returns:
        Dict[str, str]: {"UPPERCASE": "Grafia Original IBGE"}
    """
    return carregar_municipios_ibge()
