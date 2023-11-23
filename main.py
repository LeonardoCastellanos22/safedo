from ppadb.client import Client as AdbClient
import paho.mqtt.client as mqtt


APK_PATH = "./multilaser.apk"
TOPIC = "safeuem/tv"
PACKAGE_NAME = "com.apn.mobile.browser.multilaser"
HOST = "127.0.0.1"



def run(start_scanning_process):
    
    if start_scanning_process :
        print("Starting scann process to install TV agent ... ")
        client = AdbClient(host=HOST, port=5037)
        devices = client.devices()
        for device in devices:
            device_ip = device.__dict__["serial"] 
            if(not(device.is_installed(PACKAGE_NAME))):                
                print(f"App not installed, installing on this device {device_ip}")
                device = client.device(device_ip)
                is_installed = device.install(APK_PATH)
                result = "Successfully installed" if is_installed == True else "Something went wrong"
                print(result)
            else :                
                print(f"TV agent already installed on this device {device_ip}")
    
    
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT "+str(rc))
    client.subscribe(TOPIC)
    
def on_message(client, userdata, msg):
    start_scanning_process : bool = False
    start_scanning_process = True if ((msg.topic == TOPIC) and ((msg.payload) == b'1')) else False
    run(start_scanning_process)    
    
def mqtt_configuration():
    client_mqtt = mqtt.Client()
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message
    client_mqtt.connect(HOST, 1883, 60)
    client_mqtt.loop_forever()
       

mqtt_configuration()


                
        
        
        

if __name__ == "__main__":
    mqtt_configuration()
    