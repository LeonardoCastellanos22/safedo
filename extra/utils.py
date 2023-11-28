import nmap, subprocess
from ppadb.client import Client as AdbClient

APK_PATH = "./multilaser.apk"
PACKAGE_NAME = "com.apn.mobile.browser.multilaser"
HOST = "127.0.0.1"
IP_RANGE = "192.168.20.1/24"

def get_network_ips():
    nm = nmap.PortScanner()
    devices = set([])
    for loop_nmap_ips in range(2):
        nm.scan(hosts=IP_RANGE, arguments='-sn')
        devices_connected = [host for host in nm.all_hosts()]
        for device_connected in devices_connected:
            devices.add(device_connected)
    return list(devices)

def start_adb_on_devices(network_ips):
    subprocess.run(['adb', 'kill-server'], check=True)
    subprocess.run(['adb', 'start-server'], check=True)
    client = AdbClient(host=HOST, port=5037)
    for network_ip in network_ips:
        try:
            client.remote_connect(network_ip, 5555)
            client.device(f"{network_ip}:5555")
        except Exception as e:
            print(f"Error {e}")
            
    return client, client.devices()        
    

def install_apk_on_devices(client, devices, network_ips):  
    result = {"connected_devices" : [], "installed" : [], "already_installed" : [], "unauthorized":[] }    
    logs = {} 
    for i, network_ip in enumerate(network_ips):
        logs[str(i)] = {"network_ip": network_ip}
        logs[str(i)].setdefault("adb", "No")
        logs[str(i)].setdefault("tv", "No")
     
    for device in devices:
        result["connected_devices"].append(device.__dict__["serial"]) 
        device_ip = device.__dict__["serial"]
        logs = casting_log(device_ip, logs, "adb") 
        try:
            if(not(device.is_installed(PACKAGE_NAME))):                
                device = client.device(device_ip)
                is_app_installed = device.install(APK_PATH)   
                logs = casting_log(device_ip, logs, "tv")              
                result["installed"].append(device_ip) if is_app_installed == True else None
            else :
                logs = casting_log(device_ip, logs, "tv") 
                result["already_installed"].append(device_ip) 
        except Exception as e:
            result["unauthorized"].append(device_ip)
            print(f"Error {e}")
            
    
    return result, logs          
        
        
def casting_log(ip_to_check, logs, adb_tv):
    for log in logs.values():
        if log.get("network_ip") == ip_to_check[:-5]:
            log[adb_tv] = "Yes"

    return logs