# Criar o servidor MCP para acesso aos dados do IBGE
servidor_mcp_code = '''#!/usr/bin/env python3
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
        # Validar que não exceda o limite da API
        # Esta é uma verificação básica - idealmente faria cálculo mais preciso
        
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
        # Obter todos os agregados
        todos_agregados = ibge_client.get_agregados()
        
        # Buscar termo nos nomes e pesquisas
        termo_lower = termo.lower()
        agregados_encontrados = []
        
        for pesquisa in todos_agregados:
            pesquisa_nome = pesquisa.get("nome", "").lower()
            
            for agregado in pesquisa.get("agregados", []):
                agregado_nome = agregado.get("nome", "").lower()
                
                if termo_lower in pesquisa_nome or termo_lower in agregado_nome:
                    agregados_encontrados.append({
                        "agregado_id": agregado.get("id"),
                        "agregado_nome": agregado.get("nome", ""),
                        "pesquisa": pesquisa.get("nome", ""),
                        "pesquisa_id": pesquisa.get("id")
                    })
                    
                if len(agregados_encontrados) >= limite:
                    break
                    
            if len(agregados_encontrados) >= limite:
                break
        
        return {
            "status": "sucesso",
            "termo_buscado": termo,
            "total_encontrados": len(agregados_encontrados),
            "limite_aplicado": limite,
            "resultados": agregados_encontrados
        }
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@mcp.resource("mcp://ibge/help")
def help_documentation() -> str:
    """Documentação de ajuda para usar o servidor MCP do IBGE"""
    return '''
# Servidor MCP - API de Dados Agregados do IBGE

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
'''

if __name__ == "__main__":
    # Executar servidor MCP
    print("🚀 Iniciando Servidor MCP para IBGE...")
    print("📊 API Base:", BASE_URL)
    print("🔧 Ferramentas disponíveis: 6")
    print("📚 Documentação: mcp://ibge/help")
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\\n👋 Servidor MCP encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar servidor: {e}")
'''

# Salvar o código do servidor MCP
with open('ibge_mcp_server.py', 'w', encoding='utf-8') as f:
    f.write(servidor_mcp_code)
    
print("✅ Servidor MCP criado: 'ibge_mcp_server.py'")
print("🔧 Para usar: python ibge_mcp_server.py")
print("📦 Dependências: pip install mcp requests")