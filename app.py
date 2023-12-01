from flask import Flask, request, render_template, flash
from flask_bootstrap import Bootstrap 
import os, time, json
from utils import *

app = Flask(__name__)
bootstrap = Bootstrap(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/', methods=['GET', 'POST'])
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
        

if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0")
    
    