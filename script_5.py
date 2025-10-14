# Adicionar recurso de documentação e seção principal
final_code = '''
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

# Adicionar ao arquivo
with open('ibge_mcp_server.py', 'a', encoding='utf-8') as f:
    f.write(final_code)
    
print("✅ Servidor MCP completo criado!")
print("📁 Arquivo: ibge_mcp_server.py")

# Verificar tamanho do arquivo
import os
file_size = os.path.getsize('ibge_mcp_server.py')
print(f"📏 Tamanho do arquivo: {file_size} bytes")