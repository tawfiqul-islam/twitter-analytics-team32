#!/usr/bin/python

import boto
import time
from boto.ec2.regioninfo import RegionInfo

def connect():
    
    
    region=RegionInfo(name='melbourne', endpoint='nova.rc.nectar.org.au')
    
    ec2_conn = boto.connect_ec2(aws_access_key_id='741b95cd6ff9487c93feddbdf0dbdf8a',
            aws_secret_access_key='ca948c9f13d24a0e9df25d8acec5f8fb',
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
    ec2_conn.run_instances('ami-86f4a44c', placement= 'melbourne-np',
    key_name='team32KeyPair', instance_type='m2.tiny', 
    security_groups=['default'], max_count=4)
    startUpVM(ec2_conn)
    return;

def startUpVM(ec2_conn):
    reservations = ec2_conn.get_all_reservations()
    i=0
    for res in reservations:
        for ins in res.instances:
            while ins.state == "pending":
                time.sleep(5)
                ins.update()
            print 'instance ', i , ' id:', ins.id
            i=i+1   
    return;

def findMasterVM(ec2_conn):
    reservations = ec2_conn.get_all_reservations() 
    return reservations[0].instances[0].id;

def terminateVM(ec2_conn):
    return;

def createVolume(ec2_conn):
    ec2_conn.create_volume(size=100, zone='melbourne-np', volume_type='melbourne')
    return;

def findVolume(ec2_conn):
    curr_vol = ec2_conn.get_all_volumes()
    for vol in curr_vol:
        while vol.status == "pending":
            time.sleep(5)
        print 'id: ', vol.id, 'size: ', vol.size, 'zone: ', vol.zone, 'type: ', vol.type, 'status: ', vol.status, '\n'
    return vol.id;

def attachVolume(ec2_conn, v_id, ins_id):
    ec2_conn.attach_volume (volume_id=v_id, instance_id=ins_id, device='/dev/vdc')
    return;

def terminateVolume():
    return;

def main():
     
    ec2_conn=connect()
    #findImage(ec2_conn)
    createVM(ec2_conn)
    createVolume(ec2_conn)
    masterVMId=findMasterVM(ec2_conn)
    volumeId=findVolume(ec2_conn)
    attachVolume(ec2_conn, volumeId, masterVMId)
    
main()

