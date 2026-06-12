from flask import Flask, jsonify, render_template_string
import serial
import threading
import time
# pyrefly: ignore [missing-import]
import firebase_admin
# pyrefly: ignore [missing-import]
from firebase_admin import credentials
# pyrefly: ignore [missing-import]
from firebase_admin import firestore

db = None
try:
    cred = credentials.Certificate('./arduino_service.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Conexão com o Firebase estabelecida com sucesso!")
except Exception as e:
    print(f"Aviso: Não foi possível conectar ao Firebase. O arquivo 'arduino_service.json' pode estar ausente ou inválido. Erro: {e}")



app = Flask(__name__)

dados_sensor = {"distancia": "Desconhecido", "raw": 1023.0, "timestamp": " "}

PORTA_SERIAL = 'COM3'
BAUD_RATE = 9600

distancia_atual = 0.0
valor_cru_atual = 1023.0

def ler_porta_serial():
    global dados_sensor
    global distancia_atual
    global valor_cru_atual
    try:
        ser = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"Conectado ao Arduino na porta {PORTA_SERIAL}")
        
        while True:
            if ser.in_waiting > 0:
                linha = ser.readline().decode('utf-8').strip()
                
                if linha:
                    try:
                        valor_analogico = float(linha)
                        valor_cru_atual = valor_analogico
                        
                        # Converte valor analógico do sensor de umidade (0 a 1023) para porcentagem.
                        # Geralmente, 1023 é seco (0%) e cerca de 200 é totalmente úmido (100%).
                        percentual = ((1023 - valor_analogico) / (1023 - 200)) * 100
                        percentual = max(0.0, min(100.0, percentual))  # Clampa entre 0% e 100%
                        
                        distancia_atual = round(percentual, 1)
                        dados_sensor["distancia"] = distancia_atual
                        dados_sensor["raw"] = valor_cru_atual
                        
                        if db:
                            dados_sensor["timestamp"] = firestore.SERVER_TIMESTAMP
                            db.collection('historico_sensores').add(dados_sensor)
                            print(f"Dados enviados para o Firestore: {distancia_atual}% (raw: {valor_cru_atual})")
                        else:
                            dados_sensor["timestamp"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                            print(f"Dados atualizados localmente (Firebase indisponível): {distancia_atual}% (raw: {valor_cru_atual})")
                    except ValueError:
                        pass
            time.sleep(0.01)
    except Exception as e:
        print(f'Erro na comunicação Serial: {e}')
        print('Verifique se a porta está correta ou se o monitor serial da IDE não está aberto.')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitor de Umidade</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; background-color: #f4f4f9; padding-top: 100px; }
        .card { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: inline-block; }
        h1 { color: #333; margin-top: 0;}
        .valor { font-size: 5em; font-weight: bold; color: #0078D7; }
        .unidade { font-size: 0.3em; color: #666; }
        .raw-container { margin-top: 20px; font-size: 1.1em; color: #555; border-top: 1px solid #eee; padding-top: 15px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Umidade Atual</h1>
        <div class="valor" id="distancia-display">-- <span class="unidade">%</span></div>
        <div class="raw-container">
            Valor Bruto do Sensor: <strong id="raw-display">--</strong>
        </div>
    </div>

    <script>
        // Função que bate na API do Flask e atualiza o DOM a cada 500ms
        function buscarDistancia() {
            fetch('/api/dados')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('distancia-display').innerHTML = 
                        data.distancia.toFixed(1) + ' <span class="unidade">%</span>';
                    document.getElementById('raw-display').innerText = data.raw;
                })
                .catch(error => console.error('Erro de conexão:', error));
        }

        setInterval(buscarDistancia, 500);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/dados')
def api_dados():
    return jsonify({"distancia": distancia_atual, "raw": valor_cru_atual})

if __name__ == '__main__':
    thread_arduino = threading.Thread(target=ler_porta_serial, daemon=True)
    thread_arduino.start()

    print("Iniciando servidor web na porta 80...")
    app.run(host='0.0.0.0', port=80)