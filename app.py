from flask import Flask, request, render_template, flash, jsonify
from flask_bootstrap import Bootstrap
import os, time, json, glob
from utils import *

app = Flask(__name__)
bootstrap = Bootstrap(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/safetv', methods=['GET', 'POST'])
def safetv():
    context = {
        "logs" : {"0":{"network_ip":"N/A", "adb":"N/A", "tv" : "N/A"}}
    }
    if request.method == 'POST':
        ip = get_current_gateway()
        ip_range = f"{ip}/24"
        network_ips = get_network_ips(ip_range)
        print(f"Network IP {network_ips}")
        print("Starting scann process to install TV agent ... ")
        client, devices = start_adb_on_devices(network_ips)
        print("Please authorize your devices ...")
        time.sleep(30)        
        result, logs = install_apk_on_devices(client, devices, network_ips)
        print(f"Logs : {logs}")    
        context = {
            "logs" : logs
        }
        print(f"Result : {result}")
    return render_template('safetv.html', **context )

@app.route('/starting_adb_process', methods = ['GET', 'POST'])
def starting_adb_process():
    context = {}
    if request.method == 'GET' or request.method == 'POST':
        return render_template('adb_process.html', **context) 
    
@app.route('/starting_usb_adb_process', methods = ['GET', 'POST'])
def starting_usb_adb_process():
    context = {}
    if request.method == 'GET' or request.method == 'POST':
        return render_template('adb_process_usb.html', **context) 

@app.route('/full_safetv', methods=['GET', 'POST'])
def full_safetv():
    if request.method == 'POST' or request.method == 'GET':
        ip_range = "10.1.1.0/24"
        logs, network_ips = get_network_ips(ip_range)
        print(f"Network IP {network_ips}")
        print("Starting scann process to install TV agent ... ")
        connected_devices = start_adb_on_devices(network_ips)
        devices_connected_to_adb = [device.serial for device in connected_devices]
        print("Please authorize your devices ...")
        time.sleep(30)
        install_safetv_apk(devices_connected_to_adb)
        set_device_owner_on_devices(devices_connected_to_adb)
        allow_permissions_on_devices(devices_connected_to_adb)     
 
    return "Done"

@app.route('/network', methods=['GET', 'POST'])
def network_ip():
    if request.method == 'GET':
        ip = get_current_gateway()
        ip_range = f"{ip}/24"
        logs = get_network_ips(ip_range)
    return json.dumps({'success':True, 'logs' : logs}), 200, {'ContentType':'application/json'} 

@app.route('/startAdb', methods=['GET', 'POST'])
def start_adb():
    if request.method == 'POST':
        data = request.json
        network_ips = data.get('network_ips')
        print("Network from request", network_ips)
        client, devices = start_adb_on_devices(network_ips)
        devices_connected = [device.__dict__["serial"].split(':')[0] for device in devices] 
    return json.dumps({'success':True, 'devices' : devices_connected}), 200, {'ContentType':'application/json'} 

@app.route('/installApk', methods=['GET', 'POST'])
def install_apk():
    if request.method == 'POST':
        ip = get_current_gateway()
        ip_range = f"{ip}/24"
        client , devices = start_usb_adb_devices()
        start_install_do_usb_devices(devices)
       # logs, network_ips = get_network_ips(ip_range)
       # print(logs)
       # client, devices = start_adb_on_devices(['192.168.1.31'])  
       # devices_connected = [device.__dict__["serial"].split(':')[0] for device in devicezs] 
       # print('Connected to ADB', devices_connected)
        #adb_logs = matching_logs(logs, devices_connected, 'adb')
        #print(adb_logs)
        #with open ('./logs.json', 'w') as logs_json :
         #   logs_json.write(adb_logs) 
      #  result, logs, devices_with_app, devices_with_do = install_apk_on_devices(client, devices, ['192.168.1.31'])
       # devices_with_app_logs = matching_logs(adb_logs, devices_with_app, 'install')
       # devices_with_do_logs = matching_logs(devices_with_app_logs, devices_with_do, 'do')
         
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/ipregister', methods=['GET', 'POST'])
def ipregister():
    ip = get_current_gateway()
    context = {
        "ip" : ip
    }
    if request.method == 'POST':
        ip_gateway = request.form.get('ip')
        with open ('./ip.json', 'w') as json_gateway_ip:
            json_current_gateway = { "ip_gateway" : ip_gateway }
            json_object = json.dumps(json_current_gateway)
            json_gateway_ip.write(json_object)
            context = {
                "ip" : ip_gateway
            }         
            
    return render_template('ipregister.html', **context)

@app.route('/get_apks', methods=['GET'])
def get_apks():
    """Get list of available APKs"""
    try:
        apk_files = [os.path.basename(f) for f in glob.glob('./agents/*.apk')]
        current_apk = 'generic.apk'  # default
        if os.path.exists('./selected_apk.txt'):
            with open('./selected_apk.txt', 'r') as f:
                current_apk = f.read().strip()
        return jsonify({'apks': apk_files, 'current': current_apk})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/set_apk', methods=['POST'])
def set_apk():
    """Set the APK to be installed"""
    try:
        apk_name = request.form.get('apk_name') or request.json.get('apk_name')
        if not apk_name:
            return jsonify({'error': 'No APK name provided'}), 400

        apk_path = f'./agents/{apk_name}'
        if not os.path.exists(apk_path):
            return jsonify({'error': 'APK file not found'}), 404

        with open('./selected_apk.txt', 'w') as f:
            f.write(apk_name)

        return jsonify({'success': True, 'apk': apk_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/', methods=['GET', 'POST'])
def admin():
    """Admin page to manage URL configuration for the Raspberry Pi"""
    context = {}
    message = None
    error = None

    if request.method == 'POST':
        # Get form data
        hostname = request.form.get('hostname')
        tenant_name = request.form.get('tenant_name')
        instance = request.form.get('instance')
        tenant = request.form.get('tenant')
        group_id = request.form.get('group_id')

        # Update the configuration
        result = update_config_for_hostname(hostname, tenant_name, instance, tenant, group_id)

        if result.get('success'):
            message = result.get('message')
            # Update server_info.ini file
            updating_file_on_pi()
        else:
            error = result.get('error')

    # Get current configuration
    current_config = get_current_url_config()
    context['current_config'] = current_config
    context['message'] = message
    context['error'] = error

    return render_template('admin.html', **context)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=False)
    
    