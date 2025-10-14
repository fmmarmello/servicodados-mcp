# Servidor MCP para API de Dados Agregados do IBGE

Um servidor **Model Context Protocol (MCP)** que permite que LLMs (Large Language Models) acessem facilmente os dados estatísticos do **Instituto Brasileiro de Geografia e Estatística (IBGE)** através de sua API de dados agregados.

## 🎯 Objetivo

Este projeto facilita o acesso aos dados do IBGE por LLMs, eliminando a necessidade de conhecimento técnico detalhado sobre a API. Com este servidor MCP, qualquer LLM compatível pode:

- Buscar dados de população, economia, agropecuária e mais
- Consultar informações por localidade (Brasil, estados, municípios)  
- Acessar séries históricas de indicadores econômicos
- Obter metadados completos sobre pesquisas e variáveis

## 🔧 Funcionalidades

### Ferramentas Disponíveis

1. **`listar_agregados`** - Lista agregados com filtros opcionais
2. **`obter_metadados_agregado`** - Obtém metadados completos de um agregado
3. **`obter_localidades`** - Lista localidades para diferentes níveis geográficos
4. **`obter_periodos_agregado`** - Lista períodos disponíveis
5. **`consultar_dados_variaveis`** - Consulta dados das variáveis com filtros
6. **`buscar_agregados_por_termo`** - Busca agregados por palavra-chave

### Recursos

- **`mcp://ibge/help`** - Documentação completa e exemplos de uso

## 🚀 Instalação Rápida

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Opção 1: Instalação Automática

**Windows:**
```bash
install.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

### Opção 2: Instalação Manual

1. Clone ou baixe os arquivos do projeto
2. Crie um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Como Usar

### Executando o Servidor

```bash
python ibge_mcp_server.py
```

O servidor iniciará e ficará disponível para conexões MCP via STDIO.

### Integrando com Claude Desktop

1. Localize o arquivo de configuração do Claude Desktop:
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Adicione a configuração do servidor:
   ```json
   {
     "mcpServers": {
       "ibge-data": {
         "command": "python",
         "args": ["caminho/para/ibge_mcp_server.py"],
         "env": {}
       }
     }
   }
   ```

3. Reinicie o Claude Desktop

### Integrando com Cursor IDE

1. Abra as configurações do Cursor
2. Procure por "MCP Servers" 
3. Adicione a configuração do servidor IBGE

## 📊 Exemplos de Uso

### Buscar Dados de População

```
Busque dados sobre população do Brasil nos últimos anos
```

O LLM usará automaticamente: `buscar_agregados_por_termo("população")`

### Consultar PIB por Estado

```
Mostre o PIB dos estados brasileiros no último período disponível
```

### Obter Dados de Inflação

```
Quais são os índices de preços disponíveis no IBGE?
```

### Análise Regional

```
Compare a população entre as regiões metropolitanas de São Paulo e Rio de Janeiro
```

## 🗺️ Níveis Geográficos Suportados

| Código | Descrição |
|--------|-----------|
| **BR** | Brasil |
| **N1** | Grandes Regiões |
| **N2** | Unidades da Federação (Estados) |
| **N3** | Mesorregiões |
| **N6** | Municípios |
| **N7** | Regiões Metropolitanas |

## 📚 API do IBGE - Informações Técnicas

### Base URL
```
https://servicodados.ibge.gov.br/api/v3
```

### Limites da API
- Máximo de **100.000 valores** por requisição
- Fórmula: `Nº categorias × Nº períodos × Nº localidades ≤ 100.000`

### Valores Especiais nos Dados
| Símbolo | Significado |
|---------|-------------|
| **-** | Zero (não resultante de arredondamento) |
| **..** | Não se aplica |
| **...** | Dado não disponível |
| **X** | Dado omitido para evitar individualização |

## 🔍 Exemplos Avançados

### Consulta Específica com Filtros

```python
# Exemplo de consulta programática
consultar_dados_variaveis(
    agregado_id=1712,  # Produção Agrícola 
    variavel="214|1982",  # Quantidade produzida e vendida
    localidades="N2[35,33]",  # SP e RJ
    periodos="-6",  # Últimos 6 períodos
    classificacao="226[4844]"  # Abacaxi
)
```

### Pesquisas Populares

- **Agregado 1705**: Estimativas de População
- **Agregado 1712**: Produção Agrícola Municipal  
- **Agregado 5938**: Produto Interno Bruto dos Municípios
- **Agregado 7060**: Pesquisa Nacional por Amostra de Domicílios Contínua

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
├── ibge_mcp_server.py          # Servidor MCP principal
├── ibge_api_structure.json     # Estrutura mapeada da API
├── requirements.txt            # Dependências Python
├── claude_desktop_config.json  # Configuração para Claude
├── install.bat                 # Instalador Windows
├── install.sh                  # Instalador Unix
└── README.md                   # Esta documentação
```

### Tecnologias Utilizadas

- **FastMCP**: Framework para servidores MCP
- **Requests**: Cliente HTTP para Python
- **JSON**: Manipulação de dados estruturados

### Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## ❓ Solução de Problemas

### Erro "Módulo MCP não encontrado"
```bash
pip install mcp
```

### Timeout na API do IBGE
O servidor possui timeout de 30 segundos. Reduza o escopo da consulta se necessário.

### Limite de 100.000 valores excedido
Refine os filtros da consulta para reduzir o número de combinações.

## 📄 Licença

Este projeto é open source e está disponível sob a licença MIT.

## 🤝 Suporte

Para dúvidas e suporte:
- Consulte a documentação da API do IBGE
- Verifique os logs do servidor MCP
- Use a ferramenta de help: `mcp://ibge/help`

---

**Desenvolvido para facilitar o acesso aos dados oficiais do Brasil por LLMs** 🇧🇷