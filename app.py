from flask import Flask, request, render_template, flash
from flask_bootstrap import Bootstrap 
import os, time
from extra.utils import *

app = Flask(__name__)
bootstrap = Bootstrap(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/', methods=['GET', 'POST'])
def tv_interface():
    context = {
        "logs" : {}
    }
    if request.method == 'POST':
        network_ips = get_network_ips()
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

        
    
        
        
        

if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0")
    
    