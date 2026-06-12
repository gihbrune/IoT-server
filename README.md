# Monitor de Sensores IoT

## Fluxo de Dados
O projeto opera em um ciclo contínuo de monitoramento: o **sensor indutivo** captura sinais analógicos que são lidos pelo Arduino e transmitidos via **comunicação Serial** para o computador. O servidor **Flask**, rodando em Python, intercepta esses dados brutos, realiza o processamento matemático para converter a leitura em uma porcentagem de umidade e armazena o histórico no **Firebase Firestore**. Na ponta final, o **navegador do operador** executa um script JavaScript que consome a API interna do servidor via requisições assíncronas (fetch) a cada 500ms, garantindo que a interface web apresente os valores atualizados em tempo real sem a necessidade de recarregar a página.

## Requisitos
- Python 3.x
- Node.js (para Firebase Tools)
- Arduino conectado na porta `COM3`