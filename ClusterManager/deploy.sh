#!/bin/bash

path="$1" 
cd "$path"/Cluster

python setup.py

echo "VM Created"
echo "Waiting for SSh to COME UP"
sleep 300

echo "Configuring CouchDB and Deploying Harvester-->>"
sleep 5

cd "$path"/Ansible

ansible-playbook -i hosts configure-vm.yml

echo "Harvesting Started"
