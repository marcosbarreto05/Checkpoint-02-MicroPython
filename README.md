# Checkpoint 2 — ESP32 + OpenWeather + LCD + MQTT

Integrantes do grupo:
Fernanda Botejara Nellessen – RM:569761;
Enrico Giacometti Guerreiro – RM: 569700;
Marcos Vinicius de Santana Barreto – RM: 572895;
Sofia Rizzo Burigo – RM: 573751.

Projeto desenvolvido para o Checkpoint 2 — Computational Thinking for Engineering, utilizando um ESP32 com MicroPython para obter informações meteorológicas da API OpenWeather, exibir os dados em um display LCD 20x4 e enviá-los através do protocolo MQTT para um broker HiveMQ.

# Sobre o projeto

O projeto integra diferentes tecnologias de IoT para realizar a coleta, exibição e transmissão de dados meteorológicos.

O ESP32:

Conecta-se à rede Wi-Fi;
Consulta a API do OpenWeather;
Obtém:
Cidade;
Temperatura;
Umidade;
Condição climática;
Exibe as informações no LCD 20x4;
Organiza os dados em formato JSON;
Publica os dados em um broker MQTT;
Repete o processo a cada 10 segundos.

Tecnologias utilizadas
ESP32
MicroPython
Wokwi
LCD 20x4 I2C
OpenWeather API
Wi-Fi
MQTT
HiveMQ
Node-RED
JSON

# Ligações do LCD

O display LCD 20x4 utiliza comunicação I2C com o ESP32.

LCD	ESP32
GND	GND
VCC	5V
SDA	GPIO 21
SCL	GPIO 22

Configuração utilizada no código:

SDA_PIN = 21
SCL_PIN = 22
LCD_ADDR = 0x27

O LCD é inicializado como um display de 20 colunas e 4 linhas:

lcd = I2cLcd(
    i2c,
    LCD_ADDR,
    4,
    20
)

# OpenWeather

O ESP32 utiliza a API do OpenWeather para obter as informações meteorológicas.

A cidade utilizada no projeto é:

CIDADE = "Guarulhos"

A requisição utiliza:

units=metric

para obter a temperatura em graus Celsius.

Também é utilizado:

lang=pt_br

para solicitar a descrição das condições climáticas em português.

# Informações exibidas no LCD

Os dados são apresentados nas quatro linhas do display:

Guarulhos
Temp: 20.4 C
Umid: 87 %
nublado

A temperatura é apresentada com uma casa decimal:

texto_temp = "Temp: {:.1f} C".format(temperatura)

A condição climática é limitada a 20 caracteres para evitar ultrapassar o tamanho da linha do LCD:

lcd.putstr(condicao[:20])

# Comunicação MQTT

Após obter os dados da API, o ESP32 cria uma mensagem em formato JSON.

Broker
broker.hivemq.com
Porta
1883
Cliente
esp32_fiap_01
Tópico
fiap/iot/grupo01/temperatura

Configuração utilizada:

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

MQTT_CLIENT_ID = "esp32_fiap_01"

MQTT_TOPIC = "fiap/iot/grupo01/temperatura"

Formato da mensagem MQTT

Os dados são organizados em um dicionário Python:

dados = {
    "cidade": cidade,
    "temperatura": temperatura,
    "umidade": umidade,
    "condicao": condicao
}

Depois, o dicionário é convertido para JSON:

mensagem = json.dumps(dados)

Um exemplo de mensagem publicada é:

{
    "cidade": "Guarulhos",
    "temperatura": 20.37,
    "umidade": 87,
    "condicao": "nublado"
}

Essa mensagem pode ser recebida pelo Node-RED através do mesmo tópico MQTT.

# Funcionamento do programa

O programa executa as seguintes etapas:

1. Inicialização do LCD

O ESP32 configura a comunicação I2C utilizando:

SDA → GPIO 21
SCL → GPIO 22
2. Conexão com o Wi-Fi

O ESP32 utiliza a rede:

SSID: Wokwi-GUEST

Depois de estabelecer a conexão, o programa mostra o endereço IP obtido.

3. Conexão com o MQTT

O ESP32 se conecta ao broker:

broker.hivemq.com:1883
4. Consulta à OpenWeather

O ESP32 realiza uma requisição HTTP para obter os dados meteorológicos.

5. Exibição no LCD

Os dados recebidos são enviados para o display LCD 20x4.

6. Criação do JSON

Os dados são organizados em um objeto JSON.

7. Publicação MQTT

O JSON é publicado no tópico:

fiap/iot/grupo01/temperatura
8. Repetição

Após a publicação, o ESP32 aguarda:

time.sleep(10)

e realiza novamente todo o processo.

Tratamento de erros

O código possui tratamento de erros durante a consulta à API:

try:
    response = urequests.get(url)

Caso ocorra algum problema, o programa informa o erro no terminal.

Se a API não retornar o status 200, o LCD apresenta:

Erro OpenWeather
Verifique a API

Também existe tratamento de erro durante a publicação MQTT. Caso a publicação falhe, o ESP32 tenta realizar uma nova conexão com o broker.

Programa principal responsável por:

conexão Wi-Fi;
consulta à OpenWeather;
controle do LCD;
criação do JSON;
comunicação MQTT.
lcd_api.py

Biblioteca responsável pelas funções básicas de controle do LCD.

i2c_lcd.py

Biblioteca responsável pela comunicação entre o ESP32 e o LCD através do barramento I2C.

diagram.json

Arquivo utilizado pelo Wokwi para definir o circuito e as conexões dos componentes.

README.md

# Documentação do projeto.

Como executar

1. Abrir o projeto

Abra o projeto no Wokwi.

2. Configurar a API Key

No arquivo main.py, configure sua chave da OpenWeather:

API_KEY = "SUA_API_KEY"

Não publique sua API Key no GitHub. Utilize uma variável/configuração local ou substitua a chave por um valor fictício antes de enviar o código para um repositório público.

3. Configurar a cidade

Exemplo:

CIDADE = "Guarulhos"
4. Iniciar a simulação

Execute o projeto no Wokwi.

O terminal deverá mostrar informações semelhantes a:

CHECKPOINT 2 - ESP32
OpenWeather + LCD + MQTT

Conectando ao Wi-Fi...
Wi-Fi conectado!

Conectando ao broker MQTT...
MQTT conectado!

Consultando OpenWeather...

========== CLIMA ==========
Cidade: Guarulhos
Temperatura: 20.37 C
Umidade: 87 %
Condicao: nublado

JSON:
{"cidade": "Guarulhos", "temperatura": 20.37, "umidade": 87, "condicao": "nublado"}

Publicado no MQTT!

Aguardando 10 segundos...

Node-RED

O Node-RED pode ser utilizado para receber os dados publicados pelo ESP32.

O fluxo básico é:

MQTT IN → JSON → DEBUG
Configuração do MQTT IN

Broker:

broker.hivemq.com

Porta:

1883

Topic:

fiap/iot/grupo01/temperatura

Depois que o nó json interpretar a mensagem, o Node-RED poderá utilizar individualmente:

msg.payload.cidade
msg.payload.temperatura
msg.payload.umidade
msg.payload.condicao

Esses valores podem posteriormente ser utilizados para criar um dashboard.

# Objetivos do projeto

O projeto tem como objetivo demonstrar a integração entre:

Internet das Coisas (IoT);
ESP32;
MicroPython;
Comunicação I2C;
APIs REST;
JSON;
Protocolo MQTT;
Broker HiveMQ;
Node-RED.

A aplicação demonstra um fluxo completo de coleta, processamento, exibição e transmissão de dados.
