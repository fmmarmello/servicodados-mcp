import requests
import json

url = 'https://servicodados.ibge.gov.br/api/v3/agregados/10089/metadados'
print(f'Testando URL: {url}')

try:
    response = requests.get(url, timeout=30)
    print(f'Status code: {response.status_code}')
    print(f'Content-Type: {response.headers.get("content-type", "N/A")}')

    if response.status_code == 200:
        try:
            data = response.json()
            print(f'Tipo de dados: {type(data)}')
            if isinstance(data, list):
                print(f'Tamanho da lista: {len(data)}')
                if len(data) > 0:
                    print(f'Primeiro item: {data[0]}')
            else:
                print(f'Dados: {data}')
        except json.JSONDecodeError as e:
            print(f'Erro ao decodificar JSON: {e}')
            print(f'Conteúdo da resposta: {response.text[:500]}...')
    else:
        print(f'Erro HTTP: {response.status_code}')
        print(f'Conteúdo: {response.text[:500]}...')

except Exception as e:
    print(f'Erro na requisição: {e}')