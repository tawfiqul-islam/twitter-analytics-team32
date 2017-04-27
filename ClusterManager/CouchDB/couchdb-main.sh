#!/bin/sh

sudo sed -i '58,60 s/^/#/' /var/lib/dpkg/info/runit.postinst

sudo sh install-couchdb.sh

sudo apt-get install curl

sudo apt install python-pip

sudo pip install -U pip setuptools

sudo pip install --upgrade pip

sudo python -m pip install -U pip setuptools


sudo pip install couchdb


#### configuing couchdb 

echo "-->Configuring the COUCHDB"
sudo sv stop couchdb


mkdir /mnt/data

sudo mkfs.ext4 /dev/vdb

sudo mount /dev/vdb /mnt/data -t auto


sudo cp -R /home/couchdb/data/* /mnt/data

sudo chown -R couchdb:couchdb /mnt/data
sudo find /mnt/data -type d -exec chmod 0770 {} \;



sudo mkdir /home/couchdb/etc/temp
sudo mv /home/couchdb/etc/local.ini /home/couchdb/etc/temp

##########move tot the working directory

##get Ipaddress
IPAddress="$(ip route get 8.8.8.8 | awk '{print $NF; exit}')"

echo "${IPAddress}" 

sudo python3 configcouchdb.py ${IPAddress}

sudo cp local.ini /home/couchdb/etc/


sudo sv stop couchdb


sudo sv start couchdb

echo "-->COUCHDB STARTED"


echo "**COUCHDB INSTALLATION CCOMPLETED****"

sudo pip install tweepy

sudo pip install jsonpickle