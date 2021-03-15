#!/usr/bin/env python3
#
# read temperature + humidity data from the BLE sensor Sencor SWS500
#

import asyncio
import logging
import sys
import binascii
import time

from bleak import BleakClient
from bleak import _logger as logger
from bleak.uuids import uuid16_dict

uuid16_dict = {v: k for k, v in uuid16_dict.items()}

def UUID(uname):
  return "0000{0:x}-0000-1000-8000-00805f9b34fb".format(uuid16_dict.get(uname))

SYSTEM_ID_UUID = UUID("System ID")
MODEL_NBR_UUID = UUID("Model Number String")
DEVICE_NAME_UUID = UUID("Device Name")
FIRMWARE_REV_UUID = UUID("Firmware Revision String")
HARDWARE_REV_UUID = UUID("Hardware Revision String")
SOFTWARE_REV_UUID = UUID("Software Revision String")
MANUFACTURER_NAME_UUID = UUID("Manufacturer Name String")
BATTERY_LEVEL_UUID = UUID("Battery Level")
TEMP_NOTIFY_UUID = UUID("Temperature Measurement")

temp = ()

# reversed from "Sencor Meter_v1.1_apkpure.com.apk"
def temp_handler(sender, data):
  global temp
  type = int(data[0])
  count = int(data[1])
  channel2 = int(data[2])
  temperature = int(data[3]) - 40
  humidity = int(data[4])
  if count == 1:
    logger.info("[+] DATA: type={}, count={} (CURRENT), channel2={}, TEMPERATURE={}℃ , HUMIDITY={}%".format(type, count, channel2, temperature, humidity))
    temp = (temperature, humidity)
  else:
    logger.info("[+] DATA: type={}, count={} (archive), channel2={}, temperature={}℃ , humidity={}%".format(type, count, channel2, temperature, humidity))

async def run_init(address):
  async with BleakClient(address) as client:
    logger.info(f"[*] Connected: {await client.is_connected()}")
    logger.info("[*] Reading Device Info...")
    system_id = await client.read_gatt_char(SYSTEM_ID_UUID)
    system_id = ":".join(["{:02x}".format(x) for x in system_id[::-1]])
    logger.info("[+] System ID: " + system_id)
    model_number = (await client.read_gatt_char(MODEL_NBR_UUID)).decode().rstrip("\x00")
    logger.info("[+] Model Number: " + model_number)
    device_name = (await client.read_gatt_char(DEVICE_NAME_UUID)).decode().rstrip("\x00")
    logger.info("[+] Device Name: " + device_name)
    manufacturer_name = (await client.read_gatt_char(MANUFACTURER_NAME_UUID)).decode().rstrip("\x00")
    logger.info("[+] Manufacturer Name: " + manufacturer_name)
    firmware_revision = (await client.read_gatt_char(FIRMWARE_REV_UUID)).decode().rstrip("\x00")
    logger.info("[+] Firmware Revision: " + firmware_revision)
    hardware_revision = (await client.read_gatt_char(HARDWARE_REV_UUID)).decode().rstrip("\x00")
    logger.info("[+] Hardware Revision: " + hardware_revision)
    software_revision = (await client.read_gatt_char(SOFTWARE_REV_UUID)).decode().rstrip("\x00")
    logger.info("[+] Software Revision: " + software_revision)
  return (system_id, model_number, manufacturer_name, firmware_revision, hardware_revision, software_revision)

async def run(address):
  async with BleakClient(address) as client:
    logger.info(f"[*] Connected: {await client.is_connected()}")
    logger.info("[*] Reading Measurement Data")
    battery_level = int((await client.read_gatt_char(BATTERY_LEVEL_UUID))[0])
    logger.info("[+] Battery Level: {0}%".format(battery_level))
    while True:
      await client.start_notify(TEMP_NOTIFY_UUID, temp_handler)
      await asyncio.sleep(1.0)
    # await client.stop_notify(TEMP_NOTIFY_UUID)
  return temp

if __name__ == "__main__":
    address = "78:A5:04:??:??:??"
    loopdelay = 60  # in secs. -1 (or neg) means no loop

    LOG_DATA = 21

    logging.addLevelName(LOG_DATA, "DATA")
    logging.basicConfig(
      format='%(asctime)s %(levelname)-8s %(message)s',
      level=LOG_DATA,
      datefmt='%Y-%m-%d %H:%M:%S')

    logger.setLevel(logging.INFO)

    succeeded = False
    while not succeeded:
      try:
        loop = asyncio.get_event_loop()
        ret = loop.run_until_complete(run_init(address))
        succeeded = True
      except:
        logger.info("[!] Connection Error!")

    logger.log(LOG_DATA, ret)

    readagain = True
    while (loopdelay >= 0):
      while readagain:
        try:
          loop = asyncio.get_event_loop()
          ret = loop.run_until_complete(run(address))
          readagain = False
        except:
          logger.info("[!] Connection Error!")
      readagain = True
      logger.log(LOG_DATA, ret)
      logger.info("[*] Sleeping for {} secs. Looping forever...".format(loopdelay))
      time.sleep(loopdelay)
