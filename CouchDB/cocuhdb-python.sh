#!/bin/sh

sudo sed -i '58,60 s/^/#/' /var/lib/dpkg/info/runit.postinst

sh install-couchdb.sh

sudo apt-get install curl

sudo apt install python-pip

pip install -U pip setuptools

pip install --upgrade pip

python -m pip install -U pip setuptools

pip install couchdb-python-master.zip 
