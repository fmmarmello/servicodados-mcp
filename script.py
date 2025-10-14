# Vou estruturar os dados da API do IBGE extraídos para facilitar a criação do servidor MCP
import json

# Estrutura dos endpoints da API do IBGE baseada na documentação
api_structure = {
    "base_url": "https://servicodados.ibge.gov.br/api/v3",
    "endpoints": {
        "agregados": {
            "path": "/agregados",
            "description": "Obtém o conjunto de agregados, agrupados pelas respectivas pesquisas",
            "parameters": {
                "periodo": "Obtém as pesquisas cujos agregados disponibilizam resultados para o período informado",
                "assunto": "Obtém as pesquisas cujos agregados contém o assunto informado",
                "classificacao": "Obtém as pesquisas cujos agregados contém a classificação informada",
                "periodicidade": "Obtém as pesquisas cujos agregados contém a periodicidade de divulgação informada",
                "nivel": "Obtém as pesquisas cujos agregados disponibilizam resultados para o nível geográfico informado"
            }
        },
        "localidades": {
            "path": "/agregados/{agregado}/localidades/{nivel}",
            "description": "Obtém as localidades associadas ao agregado de acordo com um ou mais níveis geográficos"
        },
        "metadados": {
            "path": "/agregados/{agregado}/metadados",
            "description": "Obtém os metadados associados ao agregado"
        },
        "periodos": {
            "path": "/agregados/{agregado}/periodos",
            "description": "Obtém os períodos associados ao agregado"
        },
        "variaveis_com_periodo": {
            "path": "/agregados/{agregado}/periodos/{periodos}/variaveis/{variavel}",
            "description": "Obtém o conjunto de variáveis a partir do identificador do agregado, períodos pesquisados e identificador das variáveis"
        },
        "variaveis": {
            "path": "/agregados/{agregado}/variaveis/{variavel}",
            "description": "Funcionalmente equivalente à /agregados/{agregado}/periodos/-6/variaveis/{variavel}"
        }
    },
    "common_parameters": {
        "localidades": "Uma ou mais localidades delimitadas pelo caracter | (pipe). No caso do Brasil, o identificador é BR",
        "classificacao": "Restringe consulta usando classificações e categorias específicas",
        "view": "Modo de visualização. Pode ser OLAP ou flat"
    },
    "data_limits": {
        "max_values": 100000,
        "formula": "Nº de categorias x Nº de períodos x Nº de localidades <= 100.000"
    },
    "special_values": {
        "-": "Dado numérico igual a zero não resultante de arredondamento",
        "..": "Não se aplica dado numérico",
        "...": "Dado numérico não disponível",
        "X": "Dado numérico omitido a fim de evitar a individualização da informação"
    },
    "geographic_levels": {
        "BR": "Brasil",
        "N1": "Grandes Regiões",
        "N2": "Unidades da Federação",
        "N3": "Mesorregiões",
        "N6": "Municípios",
        "N7": "Regiões Metropolitanas"
    }
}

# Pesquisas disponíveis (conforme extraído da documentação)
pesquisas_disponiveis = [
    "Áreas Urbanizadas", "Cadastro Central de Empresas", "Censo Agropecuário",
    "Censo Demográfico", "Contagem da População", "Contas de ecossistemas: o uso da terra nos biomas brasileiros",
    "Contas de Espécies Ameaçadas", "Contas Econômicas Ambientais da Água",
    "Contas Econômicas Ambientais da Terra: Contabilidade Física",
    "Contas Econômicas Ambientais de Energia: produtos da biomassa",
    "Contas Nacionais Anuais", "Contas Nacionais Trimestrais",
    "Contribuição dos Polinizadores para as Produções Agrícola e Extrativista do Brasil",
    "Demografia das Empresas e Estatísticas de Empreendedorismo",
    "Estatísticas dos Cadastros de Microempreendedores Individuais",
    "Estimativas de População", "Fundações Privadas e Associações Sem Fins Lucrativos",
    "Indicadores de Desenvolvimento Sustentável", "Índice de Preços ao Consumidor em Real",
    "Índice de Preços ao Produtor", "Índice de Reajuste do Salário Mínimo",
    "Índice Nacional de Preços ao Consumidor", "Índice Nacional de Preços ao Consumidor Amplo",
    "Índice Nacional de Preços ao Consumidor Amplo 15", "Índice Nacional de Preços ao Consumidor Amplo Especial",
    "Índice Nacional de Preços ao Consumidor Especial", "Levantamento Sistemático da Produção Agrícola",
    "Objetivos de Desenvolvimento Sustentável", "Pesquisa Anual da Indústria da Construção",
    "Pesquisa Anual de Comércio", "Pesquisa Anual de Serviços", "Pesquisa da Pecuária Municipal",
    "Pesquisa de Assistência Médico-Sanitária", "Pesquisa de Estoques",
    "Pesquisa de Informações Básicas Municipais", "Pesquisa de Inovação",
    "Pesquisa de Orçamentos Familiares", "Pesquisa de Serviços de Hospedagem",
    "Pesquisa de Serviços de Publicidade e Promoção", "Pesquisa de Serviços de Tecnologia da Informação",
    "Pesquisa Estatísticas do Registro Civil", "Pesquisa Industrial Anual",
    "Pesquisa Industrial Anual - Empresa", "Pesquisa Industrial Anual - Produto",
    "Pesquisa Industrial Mensal - Dados Gerais", "Pesquisa Industrial Mensal - Produção Física",
    "Pesquisa Industrial Mensal de Emprego e Salário", "Pesquisa Mensal de Abate de Animais",
    "Pesquisa Mensal de Comércio", "Pesquisa Mensal de Emprego", "Pesquisa Mensal de Serviços",
    "Pesquisa Mensal do Leite", "Pesquisa Nacional de Saneamento Básico", "Pesquisa Nacional de Saúde",
    "Pesquisa Nacional de Saúde do Escolar", "Pesquisa Nacional por Amostra de Domicílios",
    "Pesquisa Nacional por Amostra de Domicílios Contínua anual",
    "Pesquisa Nacional por Amostra de Domicílios Contínua mensal",
    "Pesquisa Nacional por Amostra de Domicílios Contínua trimestral",
    "Pesquisa Trimestral do Abate de Animais", "Pesquisa Trimestral do Couro",
    "Pesquisa Trimestral do Leite", "Produção Agrícola Municipal",
    "Produção da Extração Vegetal e da Silvicultura", "Produção de Ovos de Galinha",
    "Produto Interno Bruto dos Municípios", "Projeção da População",
    "Sistema Nacional de Pesquisa de Custos e Índices da Construção Civil"
]

print("✅ Estrutura da API do IBGE mapeada com sucesso!")
print(f"📊 Total de pesquisas disponíveis: {len(pesquisas_disponiveis)}")
print(f"🔗 Endpoints principais mapeados: {len(api_structure['endpoints'])}")

# Salvar estrutura para usar no servidor MCP
with open('ibge_api_structure.json', 'w', encoding='utf-8') as f:
    json.dump(api_structure, f, indent=2, ensure_ascii=False)
    
print("📄 Arquivo 'ibge_api_structure.json' criado com sucesso!")