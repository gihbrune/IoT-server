# Ativa o ambiente virtual do Python no PowerShell
if (Test-Path "dev_iot\Scripts\Activate.ps1") {
    . .\dev_iot\Scripts\Activate.ps1
}

# Instala as dependências do Python
python -m pip install -r requirements.txt

# Instala as ferramentas do Firebase (globalmente)
npm install -g firebase-tools

# Executa a aplicação Flask
python app.py
