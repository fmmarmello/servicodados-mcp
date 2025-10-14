# Adicionar as ferramentas (tools) ao arquivo
tools_code = '''

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
'''

# Adicionar ao arquivo
with open('ibge_mcp_server.py', 'a', encoding='utf-8') as f:
    f.write(tools_code)
    
print("✅ Ferramentas básicas adicionadas")