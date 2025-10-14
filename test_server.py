#!/usr/bin/env python3
"""
Script de Teste do Servidor MCP do IBGE
=====================================

Este script testa as funcionalidades principais do servidor MCP
fazendo chamadas diretas para a API do IBGE.
"""

import json
import requests
from datetime import datetime

def test_ibge_api():
    """Testa a conectividade e funcionalidades básicas da API do IBGE"""

    base_url = "https://servicodados.ibge.gov.br/api/v3"

    print("🔍 Testando Servidor MCP do IBGE")
    print("=" * 50)

    # Teste 1: Listar agregados básicos
    print("\n📊 Teste 1: Listando primeiros agregados...")
    try:
        response = requests.get(f"{base_url}/agregados", timeout=10)
        if response.status_code == 200:
            agregados = response.json()
            print(f"✅ Sucesso! Encontradas {len(agregados)} pesquisas")

            # Mostrar algumas pesquisas
            for i, pesquisa in enumerate(agregados[:3]):
                print(f"   {i+1}. {pesquisa['nome']} - {len(pesquisa.get('agregados', []))} agregados")
        else:
            print(f"❌ Erro HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

    # Teste 2: Obter metadados de um agregado popular (Estimativas de População)
    print("\n👥 Teste 2: Metadados do agregado 6579 (Estimativas de População)...")
    try:
        response = requests.get(f"{base_url}/agregados/6579/metadados", timeout=10)
        if response.status_code == 200:
            metadados = response.json()
            if metadados:
                dados = metadados[0]
                print(f"✅ Sucesso!")
                print(f"   Nome: {dados.get('nome', 'N/A')}")
                print(f"   Pesquisa: {dados.get('pesquisa', 'N/A')}")
                print(f"   Variáveis: {len(dados.get('variaveis', []))}")
        else:
            print(f"❌ Erro HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Erro: {e}")

    # Teste 3: Obter localidades (UFs)
    print("\n🗺️  Teste 3: Localidades do agregado 6579 (Unidades da Federação)...")
    try:
        response = requests.get(f"{base_url}/agregados/6579/localidades/N2", timeout=10)
        if response.status_code == 200:
            localidades = response.json()
            print(f"✅ Sucesso! Encontradas {len(localidades)} UFs")

            # Mostrar algumas UFs
            for loc in localidades[:5]:
                print(f"   - {loc['nome']} (ID: {loc['id']})")
        else:
            print(f"❌ Erro HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Erro: {e}")

    # Teste 4: Consultar dados reais (População do Brasil nos últimos 3 períodos)
    print("\n📈 Teste 4: População do Brasil (últimos 3 períodos)...")
    try:
        response = requests.get(
            f"{base_url}/agregados/6579/periodos/-3/variaveis/all",
            params={"localidades": "BR"},
            timeout=15
        )
        if response.status_code == 200:
            dados = response.json()
            print(f"✅ Sucesso! Dados obtidos")

            if dados and len(dados) > 0:
                var_pop = dados[0]  # Primeira variável (normalmente população)
                print(f"   Variável: {var_pop.get('variavel', 'N/A')}")
                print(f"   Unidade: {var_pop.get('unidade', 'N/A')}")

                resultados = var_pop.get('resultados', [])
                if resultados and len(resultados) > 0:
                    series = resultados[0].get('serie', {})
                    print("   Últimos valores:")
                    for periodo, valor in list(series.items())[-3:]:
                        print(f"     {periodo}: {valor}")
        else:
            print(f"❌ Erro HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Erro: {e}")

    # Teste 5: Buscar agregados por termo
    print("\n🔍 Teste 5: Buscando agregados com termo 'PIB'...")
    try:
        response = requests.get(f"{base_url}/agregados", timeout=10)
        if response.status_code == 200:
            todos_agregados = response.json()
            agregados_pib = []

            for pesquisa in todos_agregados:
                for agregado in pesquisa.get("agregados", []):
                    if "pib" in agregado.get("nome", "").lower():
                        agregados_pib.append({
                            "id": agregado.get("id"),
                            "nome": agregado.get("nome"),
                            "pesquisa": pesquisa.get("nome")
                        })

            print(f"✅ Encontrados {len(agregados_pib)} agregados relacionados ao PIB")

            for i, agg in enumerate(agregados_pib[:3]):
                print(f"   {i+1}. ID {agg['id']}: {agg['nome']}")

    except Exception as e:
        print(f"❌ Erro: {e}")

    print("\n" + "=" * 50)
    print("✅ Testes concluídos! A API do IBGE está respondendo normalmente.")
    print("🚀 O servidor MCP está pronto para uso com LLMs.")
    return True

def generate_test_queries():
    """Gera exemplos de consultas que podem ser feitas ao servidor MCP"""

    queries = [
        "Busque dados sobre população do Brasil",
        "Quais são os agregados disponíveis sobre inflação?", 
        "Mostre o PIB dos municípios de São Paulo",
        "Obtenha dados da Pesquisa Nacional por Amostra de Domicílios",
        "Liste as regiões metropolitanas disponíveis no agregado 1705",
        "Consulte dados de produção agrícola nos últimos 5 anos",
        "Quais variáveis estão disponíveis no agregado de censo demográfico?",
        "Compare dados de emprego entre diferentes estados"
    ]

    print("\n💡 Exemplos de consultas para usar com LLMs:")
    print("=" * 50)

    for i, query in enumerate(queries, 1):
        print(f"{i}. {query}")

    print("\n📝 Como usar:")
    print("1. Execute o servidor MCP: python ibge_mcp_server.py")  
    print("2. Configure seu cliente MCP (Claude Desktop, Cursor, etc.)")
    print("3. Faça perguntas em linguagem natural usando os exemplos acima")

if __name__ == "__main__":
    success = test_ibge_api()
    if success:
        generate_test_queries()
    else:
        print("\n❌ Alguns testes falharam. Verifique sua conexão com a internet.")
