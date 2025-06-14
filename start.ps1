# Cria ambiente virtual se não existir
if (!(Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "✅ Ambiente virtual criado."
}

# Ativa o ambiente virtual
. .\.venv\Scripts\Activate.ps1
Write-Host "🔄 Ambiente virtual ativado."

# Instala as dependências
pip install -r requirements.txt
Write-Host "Dependências instaladas."

# Sobe o servidor FastAPI com hot reload
uvicorn app.main:app --reload