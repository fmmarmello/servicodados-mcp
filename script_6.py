# Criar arquivo de configuração para Claude Desktop
claude_config = {
    "mcpServers": {
        "ibge-data": {
            "command": "python",
            "args": ["ibge_mcp_server.py"],
            "env": {},
            "description": "Servidor MCP para acesso aos dados do IBGE"
        }
    }
}

with open('claude_desktop_config.json', 'w', encoding='utf-8') as f:
    import json
    json.dump(claude_config, f, indent=2, ensure_ascii=False)

print("✅ Configuração para Claude Desktop criada: claude_desktop_config.json")

# Criar arquivo requirements.txt
requirements = """mcp==0.9.0
requests>=2.25.0
"""

with open('requirements.txt', 'w') as f:
    f.write(requirements)

print("✅ Arquivo requirements.txt criado")

# Criar script de instalação para Windows
install_script_windows = """@echo off
echo 🚀 Instalando Servidor MCP do IBGE...

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado. Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

REM Criar ambiente virtual
echo 📦 Criando ambiente virtual...
python -m venv venv
call venv\\Scripts\\activate.bat

REM Instalar dependências
echo 📚 Instalando dependências...
pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Instalação concluída!
echo 🔧 Para executar: venv\\Scripts\\activate.bat && python ibge_mcp_server.py
pause
"""

with open('install.bat', 'w') as f:
    f.write(install_script_windows)

print("✅ Script de instalação Windows criado: install.bat")

# Criar script de instalação para Linux/Mac
install_script_unix = """#!/bin/bash
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
"""

with open('install.sh', 'w') as f:
    f.write(install_script_unix)

import os
os.chmod('install.sh', 0o755)

print("✅ Script de instalação Unix criado: install.sh")

print("\n📋 Arquivos criados:")
print("  - ibge_mcp_server.py (Servidor MCP)")
print("  - ibge_api_structure.json (Estrutura da API)")  
print("  - claude_desktop_config.json (Config para Claude)")
print("  - requirements.txt (Dependências)")
print("  - install.bat (Instalação Windows)")
print("  - install.sh (Instalação Unix)")