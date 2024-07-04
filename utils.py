import nmap, subprocess
from ppadb.client import Client as AdbClient
import json
import time

APK_PATH = "./DOAgent.apk"
PACKAGE_NAME = "com.aiuem.ladm"
HOST = "127.0.0.1"
ADB_COMMAND = "dpm set-device-owner com.aiuem.ladm/com.uem.base.receivers.MyPolicyReceiver"
def get_network_ips(ip_range):
    nm = nmap.PortScanner()
    devices = set([])
    for loop_nmap_ips in range(2):
        nm.scan(hosts=ip_range, arguments='-sn')
        devices_connected = [host for host in nm.all_hosts()]
        for device_connected in devices_connected:
            devices.add(device_connected)
    return dict.fromkeys(devices, {'adb' : False, 'install' : False, 'do' : False}), list(devices)

def start_adb_on_devices(network_ips):
    subprocess.run(['adb', 'kill-server'], check=True)
    subprocess.run(['adb', 'start-server'], check=True)
    client = AdbClient(host=HOST, port=5037)
    for network_ip in network_ips:
        try:    
            port = f'(nmap -T4 {network_ip} -p 20000-65535 | awk "/\\/tcp open/" | cut -d/ -f1)'
            port_result = subprocess.run(port, shell=True, capture_output=True, text=True)
            print(port_result)
            open_ports = port_result.stdout.split()[0]
            print(open_ports)
            command = f'adb connect {network_ip}:{open_ports}'
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=50)
           
                
            if result.returncode == 0:
                print("Comando ejecutado exitosamente")
                print(result.stdout)
            else:
                print("Error al ejecutar el comando")
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=50)
                print(result.stderr)

        except subprocess.TimeoutExpired :
            print(f'Timeout for this device')
            
    return client, client.devices()  

def start_usb_adb_devices():
    subprocess.run(['adb', 'kill-server'], check=True)
    subprocess.run(['adb', 'start-server'], check=True)
    client = AdbClient(host=HOST, port=5037)
    devices = client.devices()
    return client, devices

def start_install_do_usb_devices(devices):
    for device in devices:
        try:
            is_app_installed = device.install(APK_PATH)
            if(device.is_installed(PACKAGE_NAME)):                
                time.sleep(5)   
                adb_command = ['adb', 'shell', 'dpm', 'set-device-owner', 'com.safeuem.full/com.uem.base.receivers.MyPolicyReceiver']
                result_do_admin = subprocess.run(adb_command, capture_output=True, text=True, check=True)
                print("Command Output:")
                print(result_do_admin.stdout)
            else :
                print('Installed')
                
        except subprocess.CalledProcessError as error:
            print("Command failed with error:")
            print(error.stderr) 
            
        except Exception as e: 
            print(f"Error {e}")

def install_apk_on_devices(client, devices, network_ips):  
    result = {"connected_devices" : [], "installed" : [], "already_installed" : [], "unauthorized":[], "do_admin" : [] }    
    logs = {} 
    app_installed_on_devices = []
    set_do_on_devices = []
    
    for i, network_ip in enumerate(network_ips):
        logs[str(i)] = {"network_ip": network_ip}
        logs[str(i)].setdefault("adb", "No")
        logs[str(i)].setdefault("tv", "No")
     
    for device in devices:
        result["connected_devices"].append(device.__dict__["serial"]) 
        device_ip = device.__dict__["serial"]
        print(device_ip)
        logs = casting_log(device_ip, logs, "adb") 
        try:
            if(not(device.is_installed(PACKAGE_NAME))):                
                device = client.device(device_ip)
                is_app_installed = device.install(APK_PATH)   
                logs = casting_log(device_ip, logs, "tv")              
                result["installed"].append(device_ip) if is_app_installed == True else None
                app_installed_on_devices.append(device_ip) if is_app_installed == True else None
                adb_command = ['adb', 'shell', 'dpm', 'set-device-owner', 'com.safeuem.full/com.uem.base.receivers.MyPolicyReceiver']
                result_do_admin = subprocess.run(adb_command, capture_output=True, text=True, check=True)
                result["do_admin"].append(result_do_admin.stdout)
                set_do_on_devices.append(device_ip) if result_do_admin.returncode == 0 else None
                print("Command Output:")
                print(result_do_admin.stdout)
            else :
                logs = casting_log(device_ip, logs, "tv") 
                result["already_installed"].append(device_ip)
                
        except subprocess.CalledProcessError as error:
            print("Command failed with error:")
            #result["do_admin"].append(error.stderr)
            #print(error.stderr) 
            
        except Exception as e: 
            result["unauthorized"].append(device_ip)
            print(f"Error {e}")
    
    return result, logs, app_installed_on_devices, set_do_on_devices          
        
        
def casting_log(ip_to_check, logs, adb_tv):
    for log in logs.values():
        if log.get("network_ip") == ip_to_check[:-5]:
            log[adb_tv] = "Yes"

    return logs

def get_current_gateway():
    with open ('./ip.json', 'r') as ip_gateway:
        ip = json.load(ip_gateway)
    return ip["ip_gateway"]

def matching_logs(logs, ips_to_match, matching_type):
            
    for ip in logs:
        if ip in ips_to_match:
            logs[ip][matching_type] = 'Yes'
    return logs

if __name__ == '__main__':
    client, devices = start_adb_on_devices(['192.168.1.31'])
    
            