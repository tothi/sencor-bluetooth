#!/usr/bin/env python3

import asyncio
import logging
import sys
from bleak import BleakScanner
from bleak import BleakClient

name = "NGE76"
address = None
# address = "78:A5:04:??:??:??"

async def run_scan(name):
    address = None
    devices = await BleakScanner.discover()
    for d in devices:
        if d.name == name:
            print("[+] " + str(d))
            address = d.address
        else:
            print("[*] " + str(d))
    return address

async def print_services(mac_addr: str):
    async with BleakClient(mac_addr) as client:
        svcs = await client.get_services()
        print("[+] Connected.")
        for service in svcs:
            print("[+] " + str(service))

async def explore_services(mac_addr: str):
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(logging.INFO)
    log.addHandler(h)

    async with BleakClient(mac_addr) as client:
        for service in client.services:
            log.info(f"[Service] {service}")
            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        value = bytes(await client.read_gatt_char(char.uuid))
                        log.info(f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {value}")
                    except Exception as e:
                        log.error(f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {e}")
                else:
                    value = None
                    log.info(f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {value}")

                for descriptor in char.descriptors:
                    try:
                        value = bytes(await client.read_gatt_descriptor(descriptor.handle))
                        log.info(f"\t\t[Descriptor] {descriptor}) | Value: {value}")
                    except Exception as e:
                        log.error(f"\t\t[Descriptor] {descriptor}) | Value: {e}")


if __name__ == "__main__":

    while not address:
        loop = asyncio.get_event_loop()
        address = loop.run_until_complete(run_scan(name))
    print("[+] Sencor device {} has been identified at {}.".format(name, address))

    print("[*] Listing Services:")
    s = False
    while not s:
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(print_services(address))
            s = True
        except:
            print("[!] Connect error.")

    print("[*] Exploring Service Details:")
    s = False
    while not s:
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(explore_services(address))
            s = True
        except:
            print("[!] Connect error.")

