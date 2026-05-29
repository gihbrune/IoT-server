# Ativa o ambiente virtual do Python
source dev_iot/Scripts/activate

# Instala as dependências no ambiente virtual
pip install -r requirements.txt

# Instala as ferramentas do Firebase globalmente
npm install -g firebase-tools

# Executa a aplicação Flask usando o Python do ambiente virtual
python app.py
