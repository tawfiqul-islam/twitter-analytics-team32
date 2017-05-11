# twitter-analytics-team32
Repository for the project in Cluster and Cloud Computing Course at Unimelb.

How to deploy a Cluster in Nectar/AWS cloud:

- Download the sources in your local system
- Use the config.ini file to change the configurations on your need. You can change the number of VMs/Volumes to be created, access credentials to your cluster etc.
- Use the ClusterManager/deploy.sh file to deploy the cluster automatically depending on your configurations
- Move all the contents of the ClusterManager/Analytics to the remote machines, change the analytics configuration files and run analytics in the remote machines you want.
- Move all the contents of the ClusterManager/Web folder to the Master node, change configuration files and then run.



