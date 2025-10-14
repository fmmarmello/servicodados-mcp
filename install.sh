#!/bin/bash
echo "🚀 Instalando Servidor MCP do IBGE..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

# Criar ambiente virtual
echo "📦 Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
echo "📚 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Instalação concluída!"
echo "🔧 Para executar: source venv/bin/activate && python ibge_mcp_server.py"
