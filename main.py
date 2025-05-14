from fastapi import FastAPI
from utils import *



app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hola, mundo"}

@app.get("/get_network_ips/{ip_range}")
def get_network_ips(ip_range : str):
    logs, network_ips = get_network_ips(ip_range)
    return {"ips" : network_ips}