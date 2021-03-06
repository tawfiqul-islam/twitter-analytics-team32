#!/usr/bin/python
#This code is used to automatically Deploy a Cluster in Nectar/AWS cloud 
import boto
import time
import ConfigParser
from boto.ec2.regioninfo import RegionInfo

vmList=[];
volumeList=[];

#reading configurations
config = ConfigParser.ConfigParser()
config2 = ConfigParser.ConfigParser()
config.read("../config.ini")
AWS_ACCESS_KEY = config.get('cluster', 'AWS_ACCESS_KEY')
AWS_SECRET_KEY = config.get('cluster', 'AWS_SECRET_KEY')
IMAGE_TYPE = config.get('cluster', 'IMAGE_TYPE')
PLACEMENT = config.get('cluster', 'PLACEMENT')
VM_COUNT = config.get('cluster', 'VM_COUNT')
VOLUME_COUNT = config.get('cluster', 'VOLUME_COUNT')
SECURITY_GROUP = config.get('cluster', 'SECURITY_GROUP')
KEY_PAIR = config.get('cluster', 'KEY_PAIR')
VOLUME_SIZE1 = config.get('cluster', 'VOLUME_SIZE1')
VOLUME_SIZE2 = config.get('cluster', 'VOLUME_SIZE2')
VM_CREATE = config.get('cluster', 'VM_CREATE')
VM_TERMINATE = config.get('cluster', 'VM_TERMINATE')
VOLUME_CREATE = config.get('cluster', 'VOLUME_CREATE')
VOLUME_ATTACH = config.get('cluster', 'VOLUME_ATTACH')
VOLUME_DELETE = config.get('cluster', 'VOLUME_DELETE')

#this method is used to connect to the AWS/Nectar 
def connect():
    region=RegionInfo(name='melbourne', endpoint='nova.rc.nectar.org.au')
    
    ec2_conn = boto.connect_ec2(aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            is_secure=True,
            region=region,
            port=8773,
            path='/services/Cloud',validate_certs=False)
    return ec2_conn;

#create VMs in the cluster according to the specifications in the config.ini file
def createVM(ec2_conn):
    ec2_conn.run_instances('ami-86f4a44c', placement= PLACEMENT,
    key_name=KEY_PAIR, instance_type=IMAGE_TYPE, 
    security_groups=[SECURITY_GROUP], max_count=VM_COUNT,min_count=VM_COUNT)
    startUpVM(ec2_conn)
    return;

#start the VMs to get their IDs, also update config files for harvester and ansible hosts file
def startUpVM(ec2_conn):
    reservations = ec2_conn.get_all_reservations()
    config2.read('../Harvester/config.ini')
    f = open('../Ansible/hosts', 'w')  
    f.write('[vm]\n')
    i=0
    for res in reservations:
        for ins in res.instances:
            while ins.state == "pending":
                time.sleep(5)
                ins.update()
            print 'instance ', i , ' id:', ins.id
            vmList.append(ins.id)
            config2.set('VMTag', 'vm'+str(i+1), ins.private_ip_address)
            f.write(ins.private_ip_address+'\n')
            if(i==0):
                dburlStr="http://"+ins.private_ip_address+":5984/"
                config2.set('Harvest', 'databaseip', dburlStr)
                with open('../Harvester/config.ini', 'wb') as configfile:
                    config2.write(configfile)
            i=i+1   
    f.close() 
    return;

#terminate existing vms
def terminateVM(ec2_conn):
    ec2_conn.terminate_instances(instance_ids=vmList)
    return;

#create new volumes
def createVolume(ec2_conn):
    vsize=VOLUME_SIZE1
    i=0
    vcount=int(VOLUME_COUNT)
    while i <vcount:
        if i>1:
            vsize=VOLUME_SIZE2
        vol_req=ec2_conn.create_volume(size=vsize, zone=PLACEMENT, volume_type='melbourne')    
        vol = ec2_conn.get_all_volumes([vol_req.id])[0]
        volumeList.append(vol.id)
        while vol.status == "pending":
            time.sleep(5)
        print 'id: ', vol.id, 'size: ', vol.size, 'zone: ', vol.zone, 'type: ', vol.type, 'status: ', vol.status, '\n'  
        i=i+1   
    return;

#attach created volumes to the Vms
def attachVolume(ec2_conn):   
    i=0;
    while (i<len(volumeList)):
        ec2_conn.attach_volume (volume_id=volumeList[i], instance_id=vmList[i], device='/dev/vdb')
        i=i+1
    return;

#delete any previous volumes
def deleteVolume(ec2_conn):
    curr_vol = ec2_conn.get_all_volumes()
    for vol in curr_vol:
        ec2_conn.delete_volume(vol.id, dry_run=False)
    return;

#the main function
def main():
    ec2_conn=connect()
    if(VM_TERMINATE=="true"):
       terminateVM(ec2_conn)
    if(VOLUME_DELETE=="true"):
       deleteVolume(ec2_conn)
    if(VM_CREATE=="true"):
       createVM(ec2_conn)
    if(VOLUME_CREATE=="true"):
       createVolume(ec2_conn)
    if(VOLUME_ATTACH=="true"):    
       attachVolume(ec2_conn)

    return;
    
main();

