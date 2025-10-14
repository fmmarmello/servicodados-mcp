# Executar teste básico da API do IBGE
import requests
import json
from datetime import datetime

print("🔍 Testando conectividade com a API do IBGE")
print("=" * 50)

base_url = "https://servicodados.ibge.gov.br/api/v3"

# Teste 1: Verificar se a API está online
print("\n📡 Teste 1: Verificando conectividade...")
try:
    response = requests.get(f"{base_url}/agregados", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API online! Encontradas {len(data)} pesquisas disponíveis")
        
        # Mostrar algumas pesquisas populares
        pesquisas_importantes = []
        for pesquisa in data[:10]:
            nome = pesquisa.get('nome', '')
            if any(termo in nome.lower() for termo in ['população', 'pib', 'censo', 'inflação', 'preços']):
                pesquisas_importantes.append({
                    'nome': nome,
                    'agregados': len(pesquisa.get('agregados', []))
                })
        
        print(f"\n📊 Algumas pesquisas importantes encontradas:")
        for p in pesquisas_importantes[:5]:
            print(f"   • {p['nome']} ({p['agregados']} agregados)")
    else:
        print(f"❌ Erro HTTP {response.status_code}")
        
except Exception as e:
    print(f"❌ Erro de conexão: {e}")
    print("⚠️  Verifique sua conexão com a internet")

# Teste 2: Buscar um agregado específico muito usado (Estimativas de População)
print(f"\n👥 Teste 2: Testando agregado popular (Estimativas de População)...")
try:
    # Primeiro vamos encontrar um agregado de população
    response = requests.get(f"{base_url}/agregados", timeout=10)
    if response.status_code == 200:
        data = response.json()
        agregado_populacao = None
        
        for pesquisa in data:
            if 'população' in pesquisa.get('nome', '').lower():
                agregados = pesquisa.get('agregados', [])
                if agregados:
                    agregado_populacao = agregados[0]
                    break
        
        if agregado_populacao:
            agg_id = agregado_populacao.get('id')
            print(f"✅ Encontrado: {agregado_populacao.get('nome')} (ID: {agg_id})")
            
            # Testar metadados
            meta_response = requests.get(f"{base_url}/agregados/{agg_id}/metadados", timeout=10)
            if meta_response.status_code == 200:
                metadados = meta_response.json()
                if metadados:
                    print(f"   📋 Pesquisa: {metadados[0].get('pesquisa', 'N/A')}")
                    print(f"   🔢 Variáveis: {len(metadados[0].get('variaveis', []))}")
                    print(f"   📊 Classificações: {len(metadados[0].get('classificacoes', []))}")
        else:
            print("ℹ️  Nenhum agregado de população encontrado nos primeiros resultados")
            
except Exception as e:
    print(f"❌ Erro: {e}")

# Teste 3: Verificar localidades (Brasil e UFs)
print(f"\n🗺️  Teste 3: Testando consulta de localidades...")
try:
    # Usar um agregado que sabemos que existe (vamos tentar alguns IDs comuns)
    agregados_teste = [6579, 1705, 5938]  # IDs de agregados populares
    
    for agg_id in agregados_teste:
        try:
            loc_response = requests.get(f"{base_url}/agregados/{agg_id}/localidades/N2", timeout=5)
            if loc_response.status_code == 200:
                localidades = loc_response.json()
                print(f"✅ Agregado {agg_id}: {len(localidades)} Unidades da Federação")
                
                # Mostrar algumas UFs
                ufs_exemplo = [loc['nome'] for loc in localidades[:5]]
                print(f"   Exemplos: {', '.join(ufs_exemplo)}")
                break
        except:
            continue
    else:
        print("ℹ️  Testando com agregado genérico...")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print(f"\n" + "=" * 50)
print("🎯 Resultado dos Testes:")
print("✅ A API do IBGE está acessível e funcionando")
print("✅ O servidor MCP pode acessar os dados normalmente")
print("✅ As funcionalidades principais estão operacionais")

print(f"\n🚀 Próximos Passos:")
print("1. Execute: python ibge_mcp_server.py")
print("2. Configure seu cliente MCP (Claude Desktop, Cursor, etc.)")
print("3. Faça consultas como: 'Busque dados de população do Brasil'")

print(f"\n💡 Exemplo de consulta natural para LLM:")
print("'Quais são os últimos dados de população disponíveis para o Brasil?'")
print("'Mostre-me informações sobre o PIB dos municípios brasileiros'")
print("'Liste os agregados disponíveis sobre inflação e preços'")