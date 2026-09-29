import network
import time
import json
import urequests

from machine import Pin, I2C
from i2c_lcd import I2cLcd
from umqtt.simple import MQTTClient


# ==================================================
# CONFIGURAÇÕES DO WI-FI
# ==================================================

SSID = "Wokwi-GUEST"
PASSWORD = ""


# ==================================================
# CONFIGURAÇÕES DA OPENWEATHER
# ==================================================

API_KEY = "30486634a2c99e726ad6966288ec6ea8"

CIDADE = "Guarulhos"


# ==================================================
# CONFIGURAÇÕES MQTT
# ==================================================

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

MQTT_CLIENT_ID = "esp32_fiap_01"

MQTT_TOPIC = "fiap/iot/grupo01/temperatura"


# ==================================================
# CONFIGURAÇÃO DO LCD
# ==================================================

SDA_PIN = 21
SCL_PIN = 22

LCD_ADDR = 0x27

i2c = I2C(
    0,
    scl=Pin(SCL_PIN),
    sda=Pin(SDA_PIN),
    freq=400000
)

lcd = I2cLcd(
    i2c,
    LCD_ADDR,
    4,
    20
)


# ==================================================
# FUNÇÃO PARA CONECTAR AO WI-FI
# ==================================================

def conectar_wifi():

    wifi = network.WLAN(network.STA_IF)

    wifi.active(True)

    if not wifi.isconnected():

        print("Conectando ao Wi-Fi...")

        wifi.connect(SSID, PASSWORD)

        while not wifi.isconnected():
            time.sleep(0.5)

    print("Wi-Fi conectado!")

    print("IP:", wifi.ifconfig()[0])

    return wifi


# ==================================================
# FUNÇÃO PARA CONSULTAR A OPENWEATHER
# ==================================================

def consultar_clima():

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        "?q=" + CIDADE +
        "&appid=" + API_KEY +
        "&units=metric"
        "&lang=pt_br"
    )

    print()
    print("Consultando OpenWeather...")

    print("URL:")
    print(url)

    try:

        response = urequests.get(url)

        print("Status:", response.status_code)

        if response.status_code == 200:

            dados = response.json()

            cidade = dados["name"]

            temperatura = dados["main"]["temp"]

            umidade = dados["main"]["humidity"]

            condicao = dados["weather"][0]["description"]

            response.close()

            return cidade, temperatura, umidade, condicao

        else:

            print("Erro na API:")
            print(response.text)

            response.close()

            return None

    except Exception as erro:

        print("Erro ao consultar OpenWeather:")
        print(erro)

        return None


# ==================================================
# FUNÇÃO PARA MOSTRAR OS DADOS NO LCD
# ==================================================

def mostrar_lcd(cidade, temperatura, umidade, condicao):

    lcd.clear()

    # Linha 1
    lcd.move_to(0, 0)
    lcd.putstr(cidade[:20])

    # Linha 2
    lcd.move_to(0, 1)

    texto_temp = "Temp: {:.1f} C".format(temperatura)

    lcd.putstr(texto_temp)

    # Linha 3
    lcd.move_to(0, 2)

    texto_umid = "Umid: {} %".format(umidade)

    lcd.putstr(texto_umid)

    # Linha 4
    lcd.move_to(0, 3)

    lcd.putstr(condicao[:20])


# ==================================================
# FUNÇÃO PARA CONECTAR AO MQTT
# ==================================================

def conectar_mqtt():

    print()
    print("Conectando ao broker MQTT...")

    client = MQTTClient(
        MQTT_CLIENT_ID,
        MQTT_BROKER,
        port=MQTT_PORT
    )

    client.connect()

    print("MQTT conectado!")

    print("Broker:", MQTT_BROKER)

    print("Topico:", MQTT_TOPIC)

    return client


# ==================================================
# PROGRAMA PRINCIPAL
# ==================================================

print("================================")
print(" CHECKPOINT 2 - ESP32")
print(" OpenWeather + LCD + MQTT")
print("================================")


# Conecta ao Wi-Fi
wifi = conectar_wifi()


# Conecta ao MQTT
client = conectar_mqtt()


# ==================================================
# LOOP PRINCIPAL
# ==================================================

while True:

    clima = consultar_clima()

    if clima is not None:

        cidade, temperatura, umidade, condicao = clima

        print()
        print("========== CLIMA ==========")

        print("Cidade:", cidade)

        print("Temperatura:", temperatura, "C")

        print("Umidade:", umidade, "%")

        print("Condicao:", condicao)


        # ------------------------------------------
        # MOSTRA NO LCD
        # ------------------------------------------

        mostrar_lcd(
            cidade,
            temperatura,
            umidade,
            condicao
        )


        # ------------------------------------------
        # CRIA O JSON
        # ------------------------------------------

        dados = {
            "cidade": cidade,
            "temperatura": temperatura,
            "umidade": umidade,
            "condicao": condicao
        }


        mensagem = json.dumps(dados)


        print()
        print("JSON:")
        print(mensagem)

        # ------------------------------------------
        # PUBLICA NO MQTT
        # ------------------------------------------

        try:

            client.publish(
                MQTT_TOPIC,
                mensagem
            )

            print("Publicado no MQTT!")

        except Exception as erro:

            print("Erro MQTT:")
            print(erro)

            # Tenta reconectar
            try:
                client.connect()
                print("MQTT reconectado!")

            except:
                print("Falha ao reconectar MQTT")


    else:

        print("Nao foi possivel obter os dados.")

        lcd.clear()

        lcd.move_to(0, 0)
        lcd.putstr("Erro OpenWeather")

        lcd.move_to(0, 1)
        lcd.putstr("Verifique a API")


    print()
    print("Aguardando 10 segundos...")

    time.sleep(10)