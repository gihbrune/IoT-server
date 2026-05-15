import serial
import time

porta_usb = 'COM6'
baud_rate = 9600
arduino = serial.Serial(porta_usb, baud_rate)

try:
    ser = serial.Serial(porta_usb, baud_rate, timeout=1)
    time.sleep(2)
    print(f"Conectando a porta do Sistema Embarcado:{porta_usb}")

    while True:
        if arduino.in_waiting > 0:
            linha_bytes = arduino.readline()
            dados_styring = linha_bytes.decode('utf-8').strip()
            if dados_styring:
                print(f"Dado recebido:{dados_styring}")
except Exception as e:
    print(f"Erro na leitura: {e}")
    ultimo_dado = "Erro de conexão"

except KeyboardInterrupt:
    print("\n Programa Finalozado pelo usuário")

finally:
    if 'ardiuno' in locals() and arduino.is_open:
        arduino.close()
        print('Conexão Serial FechadQ')