import nmap, subprocess
from ppadb.client import Client as AdbClient
from logger import logger
import json
import time
import os
import socket

os.environ['PATH'] += os.pathsep + '/usr/bin'

HOSTNAME = socket.gethostname()

def get_selected_apk():
    """Get the currently selected APK path from config file"""
    try:
        if os.path.exists('./selected_apk.txt'):
            with open('./selected_apk.txt', 'r') as f:
                apk_name = f.read().strip()
                if apk_name and os.path.exists(f"./agents/{apk_name}"):
                    return f"./agents/{apk_name}"
    except Exception as e:
        logger.info(f"Error reading selected APK: {e}")
    return "./agents/tv_app.apk"  # Default fallback

def get_package_name():
    """Get the package name based on selected APK"""
    try:
        if os.path.exists('./selected_apk.txt'):
            with open('./selected_apk.txt', 'r') as f:
                apk_name = f.read().strip()
                if apk_name == 'cell_app.apk':
                    return "com.aiuem.ladm"
                elif apk_name == 'tv_app.apk':
                    return "com.safeuem.full"
    except Exception as e:
        logger.info(f"Error reading selected APK: {e}")
    return "com.safeuem.full"  # Default fallback for tv_app

APK_PATH = get_selected_apk()
PACKAGE_NAME = "com.safeuem.full"
HOST = "127.0.0.1"

def get_network_ips(ip_range):
    nm = nmap.PortScanner()
    devices = set([])
    try:
        nm.scan(hosts=ip_range, arguments='-sn')
        devices_connected = [host for host in nm.all_hosts()]
        for device_connected in devices_connected:
            devices.add(device_connected)
    except Exception as e:
        logger.info(f"Error executing nmap : {e}")
    return dict.fromkeys(devices, {'adb' : False, 'install' : False, 'do' : False}), list(devices)

def start_adb_on_devices(network_ips):
    subprocess.run(['adb', 'kill-server'], check=True)
    subprocess.run(['adb', 'start-server'], check=True)
    client = AdbClient(host=HOST, port=5037)
    for network_ip in network_ips:
        try:    
            #port = f'(nmap -T4 {network_ip} -p 20000-65535 | awk "/\\/tcp open/" | cut -d/ -f1)'
            #port_result = subprocess.run(port, shell=True, capture_output=True, text=True)
            #print(port_result)
            #open_ports = port_result.stdout.split()[0]
            #print(open_ports)
            #command = f'adb tcpip 5555'
            #result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=50)
            command = f'adb connect {network_ip}:5555'
            logger.info(f"ADB command : {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=5)
           
                
            if result.returncode == 0:
                logger.info(f"Command successfully executed : {command}" in {network_ip})
                logger.info(f"Result : {result.stdout}")
            else:
                logger.info(f"Error executing command : {command}" in {network_ip})
                logger.info(f"Result : {result.stderr}")

        except subprocess.TimeoutExpired :
            logger.info("Timeout for this device")
            
    return client.devices()  

def start_usb_adb_devices():
    try:
        
        subprocess.run(['adb', 'kill-server'], check=True)
        subprocess.run(['adb', 'start-server'], check=True)
        client = AdbClient(host=HOST, port=5037)
        devices = client.devices()
    except Exception as e :
        logger.info(f"Exception : {e}")
    return devices

def start_install_do_usb_devices(devices):
    apk_path = get_selected_apk()  # Get current APK dynamically
    package_name = get_package_name()  # Get package name dynamically
    for device in devices:
        try:
            is_app_installed = device.install(apk_path)
            if(device.is_installed(package_name)):
                time.sleep(5)
                adb_command = ['adb', 'shell', 'dpm', 'set-device-owner', f'{package_name}/com.uem.base.receivers.MyPolicyReceiver']
                result_do_admin = subprocess.run(adb_command, capture_output=True, text=True, check=True, timeout=5)
                print("Command Output:")
                print(result_do_admin.stdout)
            else :
                print('Installed')

        except subprocess.CalledProcessError as error:
            print("Command failed with error:")
            print(error.stderr)

        except Exception as e:
            print(f"Error {e}")


def install_safetv_apk(devices):
    apk_path = get_selected_apk()  # Get current APK dynamically
    client = AdbClient(host=HOST, port=5037)
    dict_response = []
    for device in devices :
        try :
            logger.info(f"Connecting to device: {device}")
            device_instance = client.device(device)
            response = device_instance.push(apk_path, "/data/local/tmp/TVAgent.apk")
            logger.info(f"Command : from {APK_PATH} - adb push /data/local/tmp/TVAgent.apk")
            logger.info(f"Push {device}: {response}")
            response = device_instance.shell(f'pm install -r -g /data/local/tmp/TVAgent.apk')
            logger.info(f"Command : adb shell pm install -r -g /data/local/tmp/TVAgent.apk")
            logger.info(f"Device {device}: {response}")
            dict_response.append({device : response})
        except Exception as e: 
            logger.info(f"Error {e}")
    return dict_response        

            
def set_device_owner_on_devices(devices):
    package_name = get_package_name()  # Get package name dynamically
    client = AdbClient(host=HOST, port=5037)
    dict_response = []
    for device in devices :
        try :
            logger.info(f"Connecting to device: {device}")
            device_instance = client.device(device)
            response = device_instance.shell(f'dpm set-device-owner {package_name}/com.uem.base.receivers.MyPolicyReceiver')
            logger.info(f"Command : adb shell dpm set-device-owner {package_name}/com.uem.base.receivers.MyPolicyReceiver")
            logger.info(f"Device {device}: {response}")
            dict_response.append({device : response})
        except Exception as e:
            logger.info(f"Error {e}")
    return dict_response
            
def allow_permissions_on_devices(devices):
    package_name = get_package_name()  # Get package name dynamically
    client = AdbClient(host=HOST, port=5037)
    response = []
    dict_response = []
    for device in devices :
        try :
            logger.info(f"Connecting to device: {device}")
            device_instance = client.device(device)
            response.append(device_instance.shell(f'appops set {package_name} WRITE_SETTINGS allow'))
            logger.info(f"Command :appops set {package_name} WRITE_SETTINGS allow ")
            response.append(device_instance.shell(f'appops set {package_name} RUN_IN_BACKGROUND allow'))
            logger.info(f"Command :appops set {package_name} RUN_IN_BACKGROUND allow ")
            response.append(device_instance.shell(f'appops set {package_name} RUN_ANY_IN_BACKGROUND allow'))
            logger.info(f"Command :appops set {package_name} RUN_ANY_IN_BACKGROUND allow ")
            response.append(device_instance.shell(f'appops set {package_name} READ_DEVICE_IDENTIFIERS allow'))
            logger.info(f"Command :appops set {package_name} READ_DEVICE_IDENTIFIERS allow ")
            response.append(device_instance.shell(f'appops set {package_name} SYSTEM_ALERT_WINDOW allow'))
            logger.info(f"Command :appops set {package_name} SYSTEM_ALERT_WINDOW allow ")
            response.append(device_instance.shell(f'appops set {package_name} REQUEST_INSTALL_PACKAGES allow'))
            logger.info(f"Command :appops set {package_name} REQUEST_INSTALL_PACKAGES allow ")
            response.append(device_instance.shell(f'appops set {package_name} READ_EXTERNAL_STORAGE allow'))
            logger.info(f"Command :appops set {package_name} READ_EXTERNAL_STORAGE allow ")
            response.append(device_instance.shell(f'appops set {package_name} WRITE_EXTERNAL_STORAGE allow'))
            logger.info(f"Command :appops set {package_name} WRITE_EXTERNAL_STORAGE allow ")
            response.append(device_instance.shell(f'appops set {package_name} MANAGE_EXTERNAL_STORAGE allow'))
            logger.info(f"Command :appops set {package_name} MANAGE_EXTERNAL_STORAGE allow ")
            response.append(device_instance.shell(f'dumpsys deviceidle whitelist +{package_name}'))
            logger.info(f"Command :dumpsys deviceidle whitelist +{package_name}")

            logger.info(f"Device {device}: {response}")
            dict_response.append({device : response})
        except Exception as e:
            logger.info(f"Error {e}")
    return dict_response

def pushing_file_using_adb(devices):
    updating_file_on_pi()
    dict_response = []
    for device in devices :
        try:
            response = subprocess.check_call(["adb", "-s", device, "push", "server_info.ini", "/sdcard/"])
            logger.info("server_info.ini pushed successfully.")
            dict_response.append({device : response})
        except Exception as e:
            logger.error(f"ADB push failed: {e}")
    return dict_response

def updating_file_on_pi():
    try:
        hostname = socket.gethostname()
        logger.info(f"Detected hostname: {hostname}")
    except Exception as e:
        logger.error(f"Could not determine hostname: {e}")
        return
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Error reading config.json: {e}")
        return

    if hostname not in config:
        logger.error(f"Hostname '{hostname}' not found in config.json")
        logger.error(f"Valid hostnames: {list(config.keys())}")
        return

    settings = config[hostname]

    try:
        with open("server_info.ini", "r") as f:
            template = f.read().strip()
    except Exception as e:
        logger.error(f"Error reading server_info.ini: {e}")
        return
    
    try:
        final_url = template.format(
            tenant_name=settings["tenant_name"],
            instance=settings["instance"],
            tenant=settings["tenant"],
            group_id=settings["group_id"]
        )
    except KeyError as e:
        logger.error(f"Missing placeholder in template: {e}")
        return
    except Exception as e:
        logger.error(f"Error formatting template: {e}")
        return

    logger.info(f"Generated URL: {final_url}")

    try:
        with open("server_info.ini", "w") as f:
            f.write(final_url)
        logger.info("Successfully updated server_info.ini")
    except Exception as e:
        logger.error(f"Failed to write server_info.ini: {e}")
        return

    logger.info("Process finished successfully.")

def install_apk_on_devices(client, devices, network_ips):
    apk_path = get_selected_apk()  # Get current APK dynamically
    package_name = get_package_name()  # Get package name dynamically
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
            if(not(device.is_installed(package_name))):
                device = client.device(device_ip)
                is_app_installed = device.install(apk_path)
                logs = casting_log(device_ip, logs, "tv")
                result["installed"].append(device_ip) if is_app_installed == True else None
                app_installed_on_devices.append(device_ip) if is_app_installed == True else None
                adb_command = ['adb', 'shell', 'dpm', 'set-device-owner', f'{package_name}/com.uem.base.receivers.MyPolicyReceiver']
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
    
            