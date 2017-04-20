#!/usr/bin/python

import boto
import time
import ConfigParser
from boto.ec2.regioninfo import RegionInfo

#reading configurations
config = ConfigParser.ConfigParser()
config.read("config.ini")
AWS_ACCESS_KEY = config.get('cluster', 'AWS_ACCESS_KEY')
AWS_SECRET_KEY = config.get('cluster', 'AWS_SECRET_KEY')
IMAGE_TYPE = config.get('cluster', 'IMAGE_TYPE')
PLACEMENT = config.get('cluster', 'PLACEMENT')
INSTANCE_COUNT = config.get('cluster', 'INSTANCE_COUNT')
SECURITY_GROUP = config.get('cluster', 'SECURITY_GROUP')
KEY_PAIR = config.get('cluster', 'KEY_PAIR')
VOLUME_SIZE = config.get('cluster', 'VOLUME_SIZE')
VOLUME_CREATE = config.get('cluster', 'VOLUME_CREATE')
VOLUME_ATTACH = config.get('cluster', 'VOLUME_ATTACH')

def connect():
    
    region=RegionInfo(name='melbourne', endpoint='nova.rc.nectar.org.au')
    
    ec2_conn = boto.connect_ec2(aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            is_secure=True,
            region=region,
            port=8773,
            path='/services/Cloud',validate_certs=False)
    return ec2_conn;

def findImage(ec2_conn):
    images = ec2_conn.get_all_images()
    for img in images:
        print 'id: ', img.id, 'name: ', img.name
    return;

def createVM(ec2_conn):
    ec2_conn.run_instances('ami-86f4a44c', placement= PLACEMENT,
    key_name=KEY_PAIR, instance_type=IMAGE_TYPE, 
    security_groups=[SECURITY_GROUP], max_count=INSTANCE_COUNT)
    startUpVM(ec2_conn)
    return;

def startUpVM(ec2_conn):
    reservations = ec2_conn.get_all_reservations()
    f = open('../Ansible/hosts', 'w')
    f.write('[webserver]\n')  
    i=0
    for res in reservations:
        for ins in res.instances:
            while ins.state == "pending":
                time.sleep(5)
                ins.update()
            print 'instance ', i , ' id:', ins.id
            f.write(ins.private_ip_address+'\n')
            i=i+1   
    f.close() 
    return;

def findMasterVM(ec2_conn):
    reservations = ec2_conn.get_all_reservations() 
    return reservations[0].instances[0].id;

def terminateVM(ec2_conn):
    return;

def createVolume(ec2_conn):
    ec2_conn.create_volume(size=VOLUME_SIZE, zone=PLACEMENT, volume_type='melbourne')
    return;

def findVolume(ec2_conn):
    curr_vol = ec2_conn.get_all_volumes()
    for vol in curr_vol:
        while vol.status == "pending":
            time.sleep(5)
        print 'id: ', vol.id, 'size: ', vol.size, 'zone: ', vol.zone, 'type: ', vol.type, 'status: ', vol.status, '\n'
    return vol.id;

def attachVolume(ec2_conn, v_id, ins_id):
    ec2_conn.attach_volume (volume_id=v_id, instance_id=ins_id, device='/dev/vdb')
    return;

def terminateVolume():
    return;

def main():
     
    ec2_conn=connect()
    startUpVM(ec2_conn)
    
    #findImage(ec2_conn)
    #===========================================================================
    # createVM(ec2_conn)
    # if(VOLUME_CREATE=='yes'):
    #     createVolume(ec2_conn)
    # if(VOLUME_ATTACH=='yes'):
    #     masterVMId=findMasterVM(ec2_conn)
    #     volumeId=findVolume(ec2_conn)
    #     attachVolume(ec2_conn, volumeId, masterVMId)
    #===========================================================================

    return;
    
main();

