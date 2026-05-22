import serial
import threading
import time

# pyrefly: ignore [missing-import]
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

PORTA_SERIAL = 'COM4' 
BAUD_RATE = 9600

distancia_atual = 0.0
def ler_porta_serial():
    global distancia_atual
    try:
        ser = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
        print(f"Conectado ao Arduino na porta {PORTA_SERIAL}")
        
        while True:
            if ser.in_waiting > 0:
                linha = ser.readline().decode('utf-8').strip()
                
                if "Distancia: Analogica -" in linha:
                    try:
                        valor_str = linha.split("-")[1].strip()
                        distancia_atual = float(valor_str)
                    except ValueError:
                        pass
    except Exception as e:
        print(f'Erro na comunicação Serial: {e}')
        print('Verifique se a porta está correta ou se o monitor serial da IDE não está aberto.')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitor de Distância HC-SR04</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; background-color: #f4f4f9; padding-top: 100px; }
        .card { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: inline-block; }
        h1 { color: #333; margin-top: 0;}
        .valor { font-size: 5em; font-weight: bold; color: #0078D7; }
        .unidade { font-size: 0.3em; color: #666; }
    </style>
</head>
<body>
    <div class="card">
        <h1>Distância Atual</h1>
        <div class="valor" id="distancia-display">-- <span class="unidade">cm</span></div>
    </div>

    <script>
        // Função que bate na API do Flask e atualiza o DOM a cada 500ms
        function buscarDistancia() {
            fetch('/api/dados')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('distancia-display').innerHTML = 
                        data.distancia.toFixed(2) + ' <span class="unidade">cm</span>';
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
    return jsonify({"distancia": distancia_atual})

if __name__ == '__main__':
    thread_arduino = threading.Thread(target=ler_porta_serial, daemon=True)
    thread_arduino.start()

    print("Iniciando servidor web na porta 80...")
    app.run(host='0.0.0.0', port=80)