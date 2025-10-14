# Adicionar ferramentas restantes e seção principal
remaining_code = '''
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
'''

# Adicionar ao arquivo
with open('ibge_mcp_server.py', 'a', encoding='utf-8') as f:
    f.write(remaining_code)
    
print("✅ Ferramentas avançadas adicionadas")