
# TV deploy using ADB

This runbook provides guidance and procedures for running a Flask project and installing the TV agent, allowing enrollment and control of TV devices using ADB over WiFi.

## How does it work ?

A Flask app will be running on the local network, and users can access this app if their device is connected to the network. When the user clicks on **Install TV Agent**, a script is executed to search for device IPs on the network. It then connects those devices to ADB and installs the TV agent.

## Requirements

To run this project, you must met the following requirements.

- Install Python3
- Install Git
- Install ADB
- Install pip3
- It's recommended to use a Linux distribution

## How to install the TV Agents using this solution ?

To run this project, please follow the steps outlined below:

- Clone this repository within a local folder.
```bash
git clone https://github.com/LeonardoCastellanos22/SafeTV.git
```
- Go to the folder where you allocated the project and create a virtual env.
```bash
python3 -m venv env
```
- Enable the virtual environment.

```bash
python3 source env/bin/activate
```
- Install the dependices of the project using the requirements file
```bash
pip3 install -r requirements.txt
```
- Run Flask using the following command
```bash
flask run --host=0.0.0.0 
```
- **TV Device Setup**:
  
Turn on the TV and connect it to the WiFi network (the same one connected to the server).
Enable developer options and the debug WiFi options.

- **Install TV Agent**:
  
Open your Flask application and click on the Install TV APK button.
- **Authorization**:

Wait while the script is executed, and don't forget to authorize the pop-up to use ADB on your TV.
- **Verification**:

Check the logs to confirm if the TV agent has been successfully installed.
