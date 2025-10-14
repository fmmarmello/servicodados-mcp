@echo off
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
call venv\Scripts\activate.bat

REM Instalar dependências
echo 📚 Instalando dependências...
pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Instalação concluída!
echo 🔧 Para executar: venv\Scripts\activate.bat && python ibge_mcp_server.py
pause
