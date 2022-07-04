# boot.py -- run on boot-up

import config
import time
import ujson
import machine
from lib.mqtt import MQTTClient

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)       # Put modem on Station mode
    if not sta_if.isconnected():                # Check if already connected
        print('connecting to network...')
        sta_if.active(True)                     # Activate network interface
        sta_if.connect(config.SSID, config.WPA2_PASSWORD)     # Your WiFi Credential
        # Check if it is connected otherwise wait
        while not sta_if.isconnected():
            pass
    # Print the IP assigned by router
    print('network config:', sta_if.ifconfig())

def sub_cb(topic, msg):
    print("Received msg")

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

def listen_mqqt_server(client):
    while True:
        try:
            client.check_msg()
        except OSError as e:
            restart_and_reconnect()
        time.sleep(1)

def start_mqtt_connection():
    try:
        client = connect_mqqt_server()
        #listen_mqqt_server(client)
        return client
    except OSError as e:
        restart_and_reconnect()

def connect_mqqt_server():
    client = MQTTClient(config.MQTT_CLIENT_ID,
                    server=config.MQTT_BROKER,
                    user=config.MQTT_USER,
                    password=config.MQTT_PASSWORD,
                    port=config.PORT,
                    ssl=True)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe("weather/temp")
    print('connected to MQTT broker')
    return client



do_connect()
from main import read_sensors_and_publish
broker = start_mqtt_connection()
read_sensors_and_publish(broker)
