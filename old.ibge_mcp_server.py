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
