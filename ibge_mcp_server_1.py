#!/usr/bin/env python3
"""
Servidor MCP para API de Dados Agregados do IBGE
==============================================

Este servidor MCP permite que LLMs acessem facilmente os dados estatísticos
do IBGE através da API de dados agregados.

Autor: Desenvolvimento para facilitar acesso de LLMs aos dados do IBGE
Data: Outubro 2025
"""

import asyncio
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import urlencode

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Instale a biblioteca MCP: pip install mcp")
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

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Faz requisição para a API do IBGE"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para {endpoint}: {e}")
            raise Exception(f"Erro ao acessar API do IBGE: {e}")

    def get_agregados(self, **filters) -> List[Dict[str, Any]]:
        """Obtém lista de agregados com filtros opcionais"""
        return self._make_request("/agregados", params=filters)

    def get_agregado_metadados(self, agregado_id: int) -> List[Dict[str, Any]]:
        """Obtém metadados de um agregado específico"""
        return self._make_request(f"/agregados/{agregado_id}/metadados")

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

# Inicializar servidor MCP
mcp = FastMCP(name="IBGE-Data-Server")
ibge_client = IBGEAPIClient()


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

        dados = metadados[0] if metadados else {}

        return {
            "status": "sucesso",
            "agregado_id": agregado_id,
            "nome": dados.get("nome", ""),
            "pesquisa": dados.get("pesquisa", ""),
            "assunto": dados.get("assunto", ""),
            "periodicidade": dados.get("periodicidade", {}),
            "nivel_territorial": dados.get("nivelTerritorial", {}),
            "variaveis": dados.get("variaveis", []),
            "classificacoes": dados.get("classificacoes", []),
            "url_sidra": dados.get("URL", "")
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
