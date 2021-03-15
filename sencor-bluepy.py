#!/usr/bin/env python3
#

from bluepy import btle

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        type = int(data[0])
        count = int(data[1])
        channel2 = int(data[2])
        temperature = int(data[3]) - 40
        humidity = int(data[4])
        print("[+] DATA: type={}, count={}, channel2={}, temperature={}℃ , humidity={}%".format(type, count, channel2, temperature, humidity))

while True:
    p = None
    while not p:
        try:
            p = btle.Peripheral("78:a5:04:??:??:??")
        except:
            print("[!] Connection error.")

    p.setDelegate(MyDelegate())

    p.writeCharacteristic(0x26, b"\x01\x00")

    try:
        while True:
            p.waitForNotifications(1.0)
    except:
        print("[+] Device disconnected. Reconnecting...")
