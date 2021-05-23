#!/usr/bin/env python3

import pygatt
import time
import ssl
import paho.mqtt.client as mqtt
import argparse

topic_root = "sencor"

parser = argparse.ArgumentParser(description='Sencor BLE <-> MQTT Gateway, uses MQTT TLS Client Certificate Authentication')
parser.add_argument("-H", "--mqtthost", type=str, default="localhost", help="MQTT host (default: localhost)")
parser.add_argument("-p", "--mqttport", type=int, default=8883, help="MQTT port (default: 8883)")
parser.add_argument("-C", "--cafile", type=str, help="MQTT TLS CA file (mandatory)", required=True)
parser.add_argument("-c", "--certfile", type=str, help="MQTT TLS Client Certificate file (mandatory)", required=True)
parser.add_argument("-k", "--keyfile", type=str, help="MQTT TLS Client Key file (mandatory)", required=True)
parser.add_argument("-d", "--delay", type=int, default=600, help="Waiting time in secs for data (default: 600)")
parser.add_argument("-m", "--mac", type=str, help="MAC address of Sencor BLE device (mandatory)", required=True)
parser.add_argument("-s", "--subtopic", type=str, default="sws_500", help="MQTT subtopic to use (default: sws_500")
args = parser.parse_args()

topic = "{}/{}".format(topic_root, args.subtopic)

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(cafile=args.cafile)
ssl_context.load_cert_chain(certfile=args.certfile, keyfile=args.keyfile)

mqttc = mqtt.Client()
mqttc.tls_set_context(context=ssl_context)
mqttc.connect(args.mqtthost, port=args.mqttport)

print("[*] MQTT: Authenticated")

def handle_data(handle, value):
    type = int(value[0])
    count = int(value[1])
    channel2 = int(value[2])
    temperature = int(value[3]) - 40
    humidity = int(value[4])
    if (type == 0) and (count == 1):
        flag = "[+] BLE DATA:"
        print("[*] MQTT: PUBLISHING to {}".format(topic))
        mqttc.connect(args.mqtthost, port=args.mqttport)
        mqttc.publish(topic+"/temperature", payload=temperature, retain=True)
        mqttc.publish(topic+"/humidity", payload=humidity, retain=True)
    else:
        flag = "[*] BLE INFO:"
    print("{} type={}, count={}, channel2={}, temperature={} , humidity={}%".format(flag, type, count, channel2, temperature, humidity))

adapter = pygatt.GATTToolBackend()

while True:
    try:
        adapter.start(reset_on_start=False)
        device = adapter.connect(args.mac, timeout=60)
        print("[*] BLE: Connected")

        device.char_write("0000fff1-0000-1000-8000-00805f9b34fb", bytearray([0x01, 0x00]), wait_for_response=False)
        print("[*] BLE: CHAR_WRITE sent")
        device.subscribe( "00002a1c-0000-1000-8000-00805f9b34fb", callback=handle_data)
        print("[*] BLE: Subscribed")

    except:
        print("[!] BLE: Exception")

    print("[*] BLE: Waiting for callbacks ({} secs)...".format(args.delay))
    time.sleep(args.delay)
    print("[*] BLE: Retrying...")
    adapter.stop()

