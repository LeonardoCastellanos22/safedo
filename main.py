from fastapi import FastAPI
from utils import *
from pydantic import BaseModel

class Adb(BaseModel):
    devices_connected_to_adb : list


app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hola, mundo"}

@app.get("/network_ips/")
def network_ips():
    logs, network_ips = get_network_ips("10.1.1.0/24")
    return {"ips" : network_ips}

@app.post("/start_wifi_adb/")
def start_wifi_adb(adb : Adb):
    connected_devices = start_adb_on_devices(adb.devices_connected_to_adb)
    devices_connected_to_adb = [device.serial for device in connected_devices]
    return {"devices_connected_to_adb" : devices_connected_to_adb}

@app.post("/install_apk/")
def install_apk(adb : Adb):
    installed_apk = install_safetv_apk(adb.devices_connected_to_adb)
    return {"installed_apk" : installed_apk}

@app.post("/set_device_owner/")
def set_device_owner(adb : Adb):
    device_owner = set_device_owner_on_devices(adb.devices_connected_to_adb)
    return {"device_owner" : device_owner}

@app.post("/device_permission/")
def device_permission(adb : Adb):
    device_permission = allow_permissions_on_devices(adb.devices_connected_to_adb)
    return {"device_permission" : device_permission}