#!/usr/bin/env python3
"""
Servidor MCP para API de Dados Agregados do IBGE
==============================================

Este servidor MCP permite que LLMs acessem facilmente os dados estatísticos
do IBGE através da API de dados agregados.

Autor: Desenvolvimento para facilitar acesso de LLMs aos dados do IBGE
Data: Outubro 2025
Versão: 1.0 (VERSÃO DEFINITIVA)
"""

import asyncio
import json
import logging
import os
import time
import unicodedata
import requests
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlencode

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("❌ Erro: Instale a biblioteca MCP")
    print("💡 Execute: pip install mcp")
    exit(1)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constantes da API do IBGE
BASE_URL = "https://servicodados.ibge.gov.br/api/v3"
MAX_VALUES_LIMIT = 100000

class IBGEAPIClient:
    """Cliente para interagir com a API do IBGE"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MCP-IBGE-Server/1.0',
            'Accept': 'application/json'
        })
        self._metadata_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_stats = {"hits": 0, "misses": 0}
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Faz requisição para a API do IBGE"""
        try:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"Fazendo requisição para: {url}")
            response = self.session.get(url, params=params, timeout=30)
            logger.info(f"Status code: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            logger.info(f"Resposta recebida: {type(data)} - {len(data) if isinstance(data, list) else 'não é lista'}")
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para {endpoint}: {e}")
            raise Exception(f"Erro ao acessar API do IBGE: {e}")
    
    def get_agregados(self, **filters) -> List[Dict[str, Any]]:
        """Obtém lista de agregados com filtros opcionais"""
        return self._make_request("/agregados", params=filters)
    
    def get_agregado_metadados(self, agregado_id: int) -> Dict[str, Any]:
        """Obtém metadados de um agregado específico"""
        cache_key = str(agregado_id)
        if cache_key in self._metadata_cache:
            self._cache_stats["hits"] += 1
            return self._metadata_cache[cache_key]

        self._cache_stats["misses"] += 1
        data = self._make_request(f"/agregados/{agregado_id}/metadados")
        # A API do IBGE às vezes responde com uma lista contendo um único item;
        # normalizamos para sempre trabalhar com um dicionário.
        if isinstance(data, list):
            if not data:
                raise Exception(f"Metadados para o agregado {agregado_id} estão vazios")
            data = data[0]
        if not isinstance(data, dict):
            raise Exception(
                f"Formato inesperado de metadados ({type(data).__name__}) para agregado {agregado_id}"
            )
        self._metadata_cache[cache_key] = data
        return data
    
    def get_localidades(self, agregado_id: int, nivel: str) -> List[Dict[str, Any]]:
        """Obtém localidades para um agregado e nível geográfico"""
        return self._make_request(f"/agregados/{agregado_id}/localidades/{nivel}")
    
    def get_periodos(self, agregado_id: int) -> List[Dict[str, Any]]:
        """Obtém períodos disponíveis para um agregado"""
        return self._make_request(f"/agregados/{agregado_id}/periodos")
    
    def get_variaveis(self, agregado_id: int, variavel: str = "all", 
                     localidades: str = "BR", periodos: Optional[str] = None,
                     classificacao: Optional[str] = None, view: str = "default") -> List[Dict[str, Any]]:
        """Obtém dados das variáveis de um agregado"""
        
        # Construir endpoint baseado se períodos foi especificado
        if periodos:
            endpoint = f"/agregados/{agregado_id}/periodos/{periodos}/variaveis/{variavel}"
        else:
            endpoint = f"/agregados/{agregado_id}/variaveis/{variavel}"
        
        # Parâmetros da query
        params = {"localidades": localidades}
        if classificacao:
            params["classificacao"] = classificacao
        if view and view != "default":
            params["view"] = view
            
        return self._make_request(endpoint, params=params)

class AgregadoSearchIndex:
    """Índice local para agilizar buscas por agregados usando termos enriquecidos."""

    def __init__(
        self,
        client: IBGEAPIClient,
        cache_filename: Optional[str] = None,
        max_metadata_per_search: int = 25,
    ):
        self.client = client
        self.max_metadata_per_search = max_metadata_per_search
        self.cache_path = (
            Path(cache_filename)
            if cache_filename
            else Path(__file__).with_name("ibge_agregado_index_cache.json")
        )
        self.index: Dict[str, Dict[str, Any]] = {}
        self._loaded = False

    @staticmethod
    def _normalize_text(value: str) -> str:
        if not value:
            return ""
        normalized = unicodedata.normalize("NFKD", value)
        ascii_text = normalized.encode("ASCII", "ignore").decode("ASCII")
        return ascii_text.lower().strip()

    def _ensure_entry(self, agregado_id: str) -> Dict[str, Any]:
        if agregado_id not in self.index:
            self.index[agregado_id] = {
                "terms": set(),
                "metadata_loaded": False,
                "last_updated": time.time(),
            }
        return self.index[agregado_id]

    def _add_term(self, entry: Dict[str, Any], text: str) -> bool:
        normalized = self._normalize_text(text)
        if not normalized:
            return False
        terms: Set[str] = entry["terms"]
        if normalized in terms:
            return False
        terms.add(normalized)
        entry["last_updated"] = time.time()
        return True

    def ensure_loaded(self) -> None:
        if self._loaded:
            return
        if self.cache_path.exists():
            try:
                with self.cache_path.open("r", encoding="utf-8") as cache_file:
                    payload = json.load(cache_file)
                for agg_id, entry in payload.get("index", {}).items():
                    terms = set(entry.get("terms", []))
                    self.index[agg_id] = {
                        "terms": terms,
                        "metadata_loaded": entry.get("metadata_loaded", False),
                        "last_updated": entry.get("last_updated", time.time()),
                    }
                logger.info(
                    "Índice de agregados carregado do disco (%s entradas)", len(self.index)
                )
            except Exception as exc:
                logger.warning("Falha ao carregar índice local: %s", exc)
        self._loaded = True

    def save(self) -> None:
        try:
            serializable_index = {
                agg_id: {
                    "terms": sorted(entry["terms"]),
                    "metadata_loaded": entry.get("metadata_loaded", False),
                    "last_updated": entry.get("last_updated", time.time()),
                }
                for agg_id, entry in self.index.items()
            }
            with self.cache_path.open("w", encoding="utf-8") as cache_file:
                json.dump({"index": serializable_index}, cache_file, ensure_ascii=False, indent=2)
        except Exception as exc:
            logger.warning("Não foi possível salvar o índice local: %s", exc)

    def build_basic_index(self, pesquisas: List[Dict[str, Any]]) -> bool:
        self.ensure_loaded()
        changed = False
        for pesquisa in pesquisas:
            pesquisa_nome = pesquisa.get("nome", "")
            for agregado in pesquisa.get("agregados", []):
                agregado_id = str(agregado.get("id"))
                entry = self._ensure_entry(agregado_id)
                if self._add_term(entry, pesquisa_nome):
                    changed = True
                if self._add_term(entry, agregado.get("nome", "")):
                    changed = True
                if self._add_term(entry, agregado.get("descricao", "")):
                    changed = True
        return changed

    def enrich_with_metadados(self, agregado_id: str) -> bool:
        entry = self._ensure_entry(agregado_id)
        if entry.get("metadata_loaded"):
            return False

        metadata = self.client.get_agregado_metadados(int(agregado_id))
        changed = False
        for field in ("nome", "pesquisa", "assunto"):
            if self._add_term(entry, metadata.get(field, "")):
                changed = True
        periodicidade = metadata.get("periodicidade", {})
        for periodo_field in ("frequencia",):
            if self._add_term(entry, periodicidade.get(periodo_field, "")):
                changed = True

        for variavel in metadata.get("variaveis", []):
            if self._add_term(entry, variavel.get("nome", "")):
                changed = True

        for classificacao in metadata.get("classificacoes", []):
            if self._add_term(entry, classificacao.get("nome", "")):
                changed = True
            for categoria in classificacao.get("categorias", []):
                if self._add_term(entry, categoria.get("nome", "")):
                    changed = True

        entry["metadata_loaded"] = True
        entry["last_updated"] = time.time()
        return True

    def _term_matches(self, entry: Dict[str, Any], normalized_term: str) -> bool:
        if not normalized_term:
            return False
        return any(normalized_term in term for term in entry.get("terms", set()))

    def pending_metadata_count(self) -> int:
        return sum(1 for entry in self.index.values() if not entry.get("metadata_loaded"))

    def search(
        self,
        termo: str,
        pesquisas: List[Dict[str, Any]],
        limite: int,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        self.ensure_loaded()
        dirty = self.build_basic_index(pesquisas)

        normalized_term = self._normalize_text(termo)
        matches: List[Tuple[int, int, Dict[str, Any]]] = []
        metadata_fetches = 0
        metadata_errors = 0
        ordem = 0

        for pesquisa in pesquisas:
            pesquisa_nome = pesquisa.get("nome", "")
            for agregado in pesquisa.get("agregados", []):
                agregado_id = str(agregado.get("id"))
                entry = self._ensure_entry(agregado_id)

                if self._term_matches(entry, normalized_term):
                    score = 0 if entry.get("metadata_loaded") else 1
                    matches.append(
                        (
                            score,
                            ordem,
                            {
                                "agregado_id": agregado.get("id"),
                                "agregado_nome": agregado.get("nome", ""),
                                "pesquisa": pesquisa_nome,
                                "pesquisa_id": pesquisa.get("id"),
                            },
                        )
                    )
                    ordem += 1
                    continue

                if (
                    normalized_term
                    and not entry.get("metadata_loaded")
                    and metadata_fetches < self.max_metadata_per_search
                ):
                    try:
                        if self.enrich_with_metadados(agregado_id):
                            dirty = True
                        metadata_fetches += 1
                    except Exception as exc:
                        metadata_errors += 1
                        logger.warning(
                            "Falha ao enriquecer índice para agregado %s: %s",
                            agregado_id,
                            exc,
                        )
                    else:
                        entry = self._ensure_entry(agregado_id)
                        if self._term_matches(entry, normalized_term):
                            matches.append(
                                (
                                    0,
                                    ordem,
                                    {
                                        "agregado_id": agregado.get("id"),
                                        "agregado_nome": agregado.get("nome", ""),
                                        "pesquisa": pesquisa_nome,
                                        "pesquisa_id": pesquisa.get("id"),
                                    },
                                )
                            )
                            ordem += 1

        if dirty:
            self.save()

        matches.sort(key=lambda item: (item[0], item[1]))
        resultados = [item[2] for item in matches[:limite]]

        stats = {
            "metadata_fetches": metadata_fetches,
            "metadata_errors": metadata_errors,
            "pendencias_indice": self.pending_metadata_count(),
        }
        return resultados, stats

# Inicializar servidor MCP e infraestrutura auxiliar
mcp = FastMCP(name="IBGE-Data-Server")
ibge_client = IBGEAPIClient()
search_index = AgregadoSearchIndex(ibge_client)

@mcp.tool()
def listar_agregados(periodo: Optional[str] = None, 
                    assunto: Optional[int] = None,
                    classificacao: Optional[int] = None,
                    periodicidade: Optional[str] = None,
                    nivel: Optional[str] = None) -> Dict[str, Any]:
    """
    Lista agregados disponíveis na API do IBGE com filtros opcionais.
    
    Args:
        periodo: Período específico (ex: "P5[202001]" para janeiro 2020 mensal)
        assunto: ID do assunto (ex: 70 para "Abate de animais")  
        classificacao: ID da classificação (ex: 12896 para "Agricultura familiar")
        periodicidade: Periodicidade (ex: "P5" para mensal)
        nivel: Nível geográfico (ex: "N6" para municípios)
    
    Returns:
        Lista de pesquisas e seus agregados
    """
    try:
        filters = {}
        if periodo:
            filters['periodo'] = periodo
        if assunto:
            filters['assunto'] = assunto
        if classificacao:
            filters['classificacao'] = classificacao
        if periodicidade:
            filters['periodicidade'] = periodicidade
        if nivel:
            filters['nivel'] = nivel
            
        resultado = ibge_client.get_agregados(**filters)
        
        return {
            "status": "sucesso",
            "total_pesquisas": len(resultado),
            "filtros_aplicados": filters,
            "dados": resultado[:10] if len(resultado) > 10 else resultado,  # Limitar para primeiros 10
            "nota": "Apenas os primeiros 10 resultados são mostrados" if len(resultado) > 10 else None
        }
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@mcp.tool()
def obter_metadados_agregado(agregado_id: int) -> Dict[str, Any]:
    """
    Obtém metadados completos de um agregado específico.
    
    Args:
        agregado_id: ID do agregado (ex: 1705, 1712)
    
    Returns:
        Metadados do agregado incluindo variáveis, classificações e períodos
    """
    try:
        metadados = ibge_client.get_agregado_metadados(agregado_id)

        if not metadados:
            return {"status": "erro", "mensagem": f"Agregado {agregado_id} não encontrado"}
        
        return {
            "status": "sucesso",
            "agregado_id": agregado_id,
            "nome": metadados.get("nome", ""),
            "pesquisa": metadados.get("pesquisa", ""),
            "assunto": metadados.get("assunto", ""),
            "periodicidade": metadados.get("periodicidade", {}),
            "nivel_territorial": metadados.get("nivelTerritorial", {}),
            "variaveis": metadados.get("variaveis", []),
            "classificacoes": metadados.get("classificacoes", []),
            "url_sidra": metadados.get("URL", "")
        }
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@mcp.tool()
def obter_localidades(agregado_id: int, nivel: str) -> Dict[str, Any]:
    """
    Obtém localidades disponíveis para um agregado em determinado nível geográfico.
    
    Args:
        agregado_id: ID do agregado
        nivel: Nível geográfico (N1=Grandes Regiões, N2=UF, N6=Municípios, N7=Regiões Metropolitanas)
               Pode usar múltiplos níveis separados por | (ex: "N7|N6")
    
    Returns:
        Lista de localidades disponíveis
    """
    try:
        localidades = ibge_client.get_localidades(agregado_id, nivel)
        
        return {
            "status": "sucesso",
            "agregado_id": agregado_id,
            "nivel_geografico": nivel,
            "total_localidades": len(localidades),
            "localidades": localidades[:20] if len(localidades) > 20 else localidades,
            "nota": "Apenas as primeiras 20 localidades são mostradas" if len(localidades) > 20 else None
        }
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@mcp.tool()
def obter_periodos_agregado(agregado_id: int) -> Dict[str, Any]:
    """
    Obtém todos os períodos disponíveis para um agregado.
    
    Args:
        agregado_id: ID do agregado
    
    Returns:
        Lista de períodos disponíveis com suas representações textuais
    """
    try:
        periodos = ibge_client.get_periodos(agregado_id)
        
        return {
            "status": "sucesso",
            "agregado_id": agregado_id,
            "total_periodos": len(periodos),
            "periodos": periodos[-10:] if len(periodos) > 10 else periodos,  # Mostrar últimos 10
            "nota": "Apenas os últimos 10 períodos são mostrados" if len(periodos) > 10 else None
        }
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@mcp.tool()
def consultar_dados_variaveis(agregado_id: int,
                             variavel: str = "all",
                             localidades: str = "BR", 
                             periodos: Optional[str] = None,
                             classificacao: Optional[str] = None,
                             view: str = "default") -> Dict[str, Any]:
    """
    Consulta dados das variáveis de um agregado com filtros específicos.
    
    Args:
        agregado_id: ID do agregado
        variavel: ID da variável ou "all" para todas (ex: "214|1982" para múltiplas)
        localidades: Localidades (ex: "BR", "N6[3550308]", "N7[3501,3301]") 
        periodos: Períodos específicos (ex: "-6" para últimos 6, "201701-201706" para intervalo)
        classificacao: Classificações (ex: "226[4844]|218[4780]")
        view: Modo de visualização ("OLAP", "flat" ou "default")
    
    Returns:
        Dados das variáveis consultadas
    """
    try:
        dados = ibge_client.get_variaveis(
            agregado_id=agregado_id,
            variavel=variavel,
            localidades=localidades, 
            periodos=periodos,
            classificacao=classificacao,
            view=view
        )
        
        return {
            "status": "sucesso",
            "agregado_id": agregado_id,
            "parametros": {
                "variavel": variavel,
                "localidades": localidades,
                "periodos": periodos,
                "classificacao": classificacao,
                "view": view
            },
            "total_variaveis": len(dados),
            "dados": dados,
            "observacao": "Valores especiais: '-'=zero, '..'=não se aplica, '...'=não disponível, 'X'=omitido"
        }
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@mcp.tool()
def buscar_agregados_por_termo(termo: str, limite: int = 10) -> Dict[str, Any]:
    """
    Busca agregados que contenham um termo específico no nome ou pesquisa.
    
    Args:
        termo: Termo a ser buscado (ex: "população", "inflação", "PIB")
        limite: Número máximo de resultados (padrão: 10)
    
    Returns:
        Lista de agregados encontrados
    """
    try:
        if limite <= 0:
            limite = 10

        todos_agregados = ibge_client.get_agregados()
        resultados, stats = search_index.search(termo, todos_agregados, limite)

        nota_partes: List[str] = []
        if stats.get("metadata_fetches"):
            nota_partes.append(
                f"Metadados adicionais carregados para {stats['metadata_fetches']} agregado(s) durante esta busca."
            )
        if (
            stats.get("pendencias_indice")
            and stats.get("metadata_fetches", 0) >= search_index.max_metadata_per_search
        ):
            nota_partes.append(
                "O índice ainda está sendo enriquecido; refaça a busca ou refine o termo para melhorar os resultados."
            )
        if stats.get("metadata_errors"):
            nota_partes.append(
                f"Ocorreram {stats['metadata_errors']} erro(s) ao carregar metadados; consulte os logs para detalhes."
            )

        return {
            "status": "sucesso",
            "termo_buscado": termo,
            "total_encontrados": len(resultados),
            "limite_aplicado": limite,
            "resultados": resultados,
            "indice": {
                "pendencias_metadados": stats.get("pendencias_indice", 0),
                "metadata_carregados": stats.get("metadata_fetches", 0),
            },
            "nota": " ".join(nota_partes) if nota_partes else None
        }
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@mcp.resource("mcp://ibge/help")
def help_documentation() -> str:
    """Documentação de ajuda para usar o servidor MCP do IBGE"""
    help_text = """# Servidor MCP - API de Dados Agregados do IBGE

Este servidor MCP fornece acesso simplificado aos dados estatísticos do IBGE.

## Ferramentas Disponíveis:

### 1. listar_agregados
- Lista agregados com filtros opcionais
- Parâmetros: periodo, assunto, classificacao, periodicidade, nivel

### 2. obter_metadados_agregado  
- Obtém metadados completos de um agregado
- Parâmetro: agregado_id (obrigatório)

### 3. obter_localidades
- Lista localidades para um agregado e nível geográfico
- Parâmetros: agregado_id, nivel (N1=Regiões, N2=UF, N6=Municípios)

### 4. obter_periodos_agregado
- Lista períodos disponíveis para um agregado
- Parâmetro: agregado_id

### 5. consultar_dados_variaveis
- Consulta dados das variáveis com filtros
- Parâmetros: agregado_id, variavel, localidades, periodos, classificacao

### 6. buscar_agregados_por_termo
- Busca agregados por termo no nome
- Parâmetros: termo, limite

## Exemplos de Uso:

1. Buscar dados de população:
   `buscar_agregados_por_termo("população")`

2. Obter metadados do agregado 1705:
   `obter_metadados_agregado(1705)`

3. Consultar dados do PIB para o Brasil nos últimos 6 períodos:
   `consultar_dados_variaveis(1705, "all", "BR", "-6")`

## Níveis Geográficos:
- BR: Brasil
- N1: Grandes Regiões  
- N2: Unidades da Federação
- N6: Municípios
- N7: Regiões Metropolitanas

## Valores Especiais:
- "-": Zero (não resultante de arredondamento)
- "..": Não se aplica
- "...": Dado não disponível
- "X": Dado omitido
"""
    return help_text

if __name__ == "__main__":
    # Executar servidor MCP
    print("Iniciando Servidor MCP para IBGE...")
    print("API Base:", BASE_URL)
    print("Ferramentas disponíveis: 6")
    print("Documentação: mcp://ibge/help")
    print("=" * 50)

    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\nServidor MCP encerrado pelo usuário")
    except Exception as e:
        print(f"Erro ao executar servidor: {e}")
