# Exemplos Práticos de Uso do Servidor MCP do IBGE

Este documento contém exemplos práticos de como usar o servidor MCP do IBGE com diferentes LLMs.

## 🤖 Consultas de Exemplo

### 1. Consultas Básicas sobre População

**Usuário:** "Busque dados sobre população do Brasil"

**LLM usa automaticamente:** `buscar_agregados_por_termo("população")`

**Resultado:** Lista de agregados relacionados à população, incluindo:
- Estimativas de População
- Censo Demográfico  
- Contagem da População
- Projeção da População

---

### 2. Consulta de Metadados Específicos

**Usuário:** "Me dê mais informações sobre o agregado de estimativas de população"

**LLM usa:** `obter_metadados_agregado(6579)` (ou ID encontrado)

**Resultado:** Metadados completos incluindo:
- Nome da pesquisa
- Variáveis disponíveis
- Classificações
- Periodicidade
- Níveis territoriais

---

### 3. Dados Geográficos

**Usuário:** "Quais estados têm dados de população disponíveis?"

**LLM usa:** `obter_localidades(6579, "N2")`

**Resultado:** Lista de todas as 27 Unidades da Federação com seus códigos IBGE

---

### 4. Consulta de Dados Reais

**Usuário:** "Qual foi a população do Brasil nos últimos 3 anos?"

**LLM usa:** `consultar_dados_variaveis(6579, "all", "BR", "-3")`

**Resultado:** Dados populacionais do Brasil nos últimos 3 períodos disponíveis

---

### 5. Comparação Regional

**Usuário:** "Compare a população entre São Paulo e Rio de Janeiro"

**LLM usa:** `consultar_dados_variaveis(6579, "all", "N2[35,33]", "-1")`

**Resultado:** Dados populacionais mais recentes de SP (35) e RJ (33)

---

### 6. Busca por Tema Específico

**Usuário:** "Encontre dados sobre inflação e preços"

**LLM usa:** `buscar_agregados_por_termo("preços")`

**Resultado:** Agregados como:
- Índice Nacional de Preços ao Consumidor (INPC)
- Índice Nacional de Preços ao Consumidor Amplo (IPCA)
- Índice de Preços ao Produtor (IPP)

---

## 🎯 Fluxos de Trabalho Complexos

### Análise Demográfica Completa

**Usuário:** "Faça uma análise demográfica completa do Nordeste brasileiro"

**LLM executará sequencialmente:**
1. `buscar_agregados_por_termo("população")`
2. `obter_localidades(ID_AGREGADO, "N2")` 
3. `consultar_dados_variaveis(ID_AGREGADO, "all", "N1[2]", "-5")`
4. Análise e síntese dos dados obtidos

---

### Comparação Econômica Entre Regiões

**Usuário:** "Compare o PIB per capita entre Sul e Sudeste nos últimos 5 anos"

**LLM executará:**
1. `buscar_agregados_por_termo("PIB")`
2. `obter_metadados_agregado(ID_PIB)`
3. `consultar_dados_variaveis(ID_PIB, "variavel_pib_per_capita", "N1[4,3]", "-5")`
4. Análise comparativa dos resultados

---

## 🔧 Configuração no Claude Desktop

1. Localizar arquivo de configuração:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Adicionar configuração:
```json
{
  "mcpServers": {
    "ibge-data": {
      "command": "python",
      "args": ["C:\\caminho\\para\\ibge_mcp_server.py"],
      "env": {}
    }
  }
}
```

3. Reiniciar o Claude Desktop

---

## 🔧 Configuração no Cursor IDE

1. Abrir Configurações (Ctrl/Cmd + ,)
2. Procurar "MCP" ou "Model Context Protocol"
3. Adicionar servidor:
   - Nome: `IBGE Data Server`
   - Comando: `python`
   - Argumentos: `["/caminho/para/ibge_mcp_server.py"]`

---

## 💡 Dicas de Uso

### Para Consultas Eficientes
- Seja específico sobre o período desejado
- Mencione a localidade de interesse
- Use termos claros (população, PIB, inflação, etc.)

### Consultas Recomendadas
- "Dados mais recentes de..."
- "Histórico dos últimos X anos de..."
- "Compare [localidade A] com [localidade B] em..."
- "Quais variáveis estão disponíveis para..."

### Evite Consultas Muito Amplas
- Em vez de "todos os dados do IBGE"
- Use "dados de população por estado"
- Ou "índices de preços dos últimos 12 meses"

---

## 📊 Dados Disponíveis

### Principais Pesquisas
- **Demografia:** População, censo, projeções
- **Economia:** PIB, inflação, preços, emprego
- **Agropecuária:** Produção agrícola, pecuária
- **Social:** Domicílios, educação, saúde
- **Regional:** Dados por UF, município, região

### Periodicidades
- **Anual:** PIB, Censo Agropecuário
- **Trimestral:** PIB trimestral, emprego
- **Mensal:** Inflação, produção industrial
- **Decenal:** Censo Demográfico

### Níveis Geográficos
- **Nacional:** Brasil (BR)
- **Regional:** 5 Grandes Regiões (N1)
- **Estadual:** 27 UFs (N2)
- **Municipal:** 5.570 municípios (N6)
- **Metropolitano:** Regiões Metropolitanas (N7)

---

## 🚀 Casos de Uso Avançados

### Para Pesquisadores
- Análises longitudinais de indicadores socioeconomicos
- Comparações regionais sistemáticas
- Construção de séries históricas customizadas

### Para Jornalistas
- Verificação rápida de dados oficiais
- Contextualização de notícias com estatísticas
- Análises regionais para reportagens

### Para Analistas
- Dashboards automatizados com dados atualizados
- Relatórios comparativos entre localidades
- Monitoramento de indicadores específicos

### Para Estudantes
- Acesso facilitado a dados para trabalhos acadêmicos
- Exploração de diferentes perspectivas dos dados
- Compreensão da estrutura das pesquisas oficiais

---

*O servidor MCP do IBGE torna os dados oficiais do Brasil acessíveis através de linguagem natural, democratizando o acesso à informação estatística de qualidade.*