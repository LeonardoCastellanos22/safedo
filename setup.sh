#!/bin/bash
sudo apt install -y ansible
sudo ansible-playbook -i inventory.ini playbook.yml
