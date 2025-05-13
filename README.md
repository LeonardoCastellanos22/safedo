# Android devices deploy using ADB

This runbook provides guidance and procedures for running a Flask project, allowing enrollment and control of android devices using ADB over WiFi.

## How does it work ?

A Flask app will run on the local network, and users will be able to access it if their devices are connected to the network. The Flask app will run continuously, and an access point will also be created if the device supports this feature. Once the project is up and running on the device, the script to enroll Android devices will be available to everyone on the network.

## Requirements

To run this project, you must met the following requirements.

- Install Git
- It's recommended to use a Linux distribution

## How to install the TV Agents using this solution ?

To run this project, please follow the steps outlined below:

- Clone this repository within a local folder.
```bash
git clone https://github.com/LeonardoCastellanos22/SafeTV.git
```
- Go to the folder where you allocated the project and run the following commands.
```bash
chmod +x setup.sh
./setup.sh
```

- **Device Setup**:
  
A full guide to bootstrap and use this solution will be shared once the customer has active licenses.