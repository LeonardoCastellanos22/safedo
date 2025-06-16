from fastapi import FastAPI, HTTPException
from utils import *
from pydantic import BaseModel
from logger import logger
from fastapi.middleware.cors import CORSMiddleware

class Adb(BaseModel):
    devices_connected_to_adb : list


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins= ["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hola, mundo"}

@app.get("/network_ips/")
def network_ips():
    try :
        logger.info("GET request to network_ips")
        logger.info("Scanning network 10.1.1.0/24")
        logs, network_ips = get_network_ips("10.1.1.0/24")
        logger.info(f"Network Ips scanned : {network_ips}")
        return {"ips" : network_ips}
    except Exception as e :
        logger.info("Error:", e)
        raise HTTPException(status_code=500, detail="Install failure")
    
@app.post("/start_wifi_adb/")
def start_wifi_adb(adb : Adb):
    try:
        logger.info("POST request to start_wifi_adb")
        connected_devices = start_adb_on_devices(adb.devices_connected_to_adb)
        devices_connected_to_adb = [device.serial for device in connected_devices]
        logger.info(f"Devices connected to ADB : {devices_connected_to_adb}")
        return {"devices_connected_to_adb" : devices_connected_to_adb}
    except Exception as e:
        logger.info("Error:", e)
        raise HTTPException(status_code=500, detail="ADB failure")

@app.post("/install_apk/")
def install_apk(adb : Adb):
    try:
        logger.info("POST request to install_apk")
        installed_apk = install_safetv_apk(adb.devices_connected_to_adb)
        logger.info(f"Install APK on devices : {installed_apk}")
        return {"installed_apk" : installed_apk}
    except Exception as e :
        logger.info("Error:", e)
        raise HTTPException(status_code=500, detail="Install failure")

@app.post("/set_device_owner/")
def set_device_owner(adb : Adb):
    try:
        logger.info("POST request to set_device_owner")
        device_owner = set_device_owner_on_devices(adb.devices_connected_to_adb)
        logger.info(f"Set device owner on devices : {device_owner}")
        return {"device_owner" : device_owner}
    except Exception as e :
        logger.info("Error:", e)
        raise HTTPException(status_code=500, detail="DO failure")
    
@app.post("/device_permission/")
def device_permission(adb : Adb):
    try:
        logger.info("POST request to device_permission")
        device_permission = allow_permissions_on_devices(adb.devices_connected_to_adb)
        logger.info(f"Set permissions on devices : {device_permission}")
        return {"device_permission" : device_permission}
    except Exception as e :
        logger.info("Error:", e)
        raise HTTPException(status_code=500, detail="Permissions failure")