# nornir

Show example of running Nornir via a REST API.

## To run on Kriten:

Where $KRITEN_URL is set to the URL of your Kriten instance.

1. Login
```console
curl -c ./token.txt -X POST $KRITEN_URL'/api/v1/login' \
--header 'Content-Type: application/json' \
--data '{
  "username": "root",
  "password": "root",
  "provider": "local"
}' 
```
2. Create a runner which references a Python image and the git repository.
```console
curl -b ./token.txt -X POST $KRITEN_URL'/api/v1/runners' \
--header 'Content-Type: application/json' \
--data '{
  "name": "nornir-3.5.0",
  "image": "kubecodeio/nornir:3.5.0",
  "gitURL": "https://github.com/kriten-io/kriten-community-toolkit.git",
  "branch": "main"
}'
```
3. Create a task that references the runner and the command to run the script.
```console
curl -b ./token.txt -X POST $KRITEN_URL'/api/v1/tasks' \
--header 'Content-Type: application/json' \
--data '{
  "name": "nornir-sh-ip-int",
  "command": "cd nornit; python sh-ip-int.py",
  "runner": "nornir-3.5.0"
}'
```
4. Launch job.
```console
curl -b ./token.txt -X POST $KRITEN_URL'/api/v1/jobs/nornir-sh-ip-int' \
--header 'Content-Type: application/json' \
--data '{
  "group": "LEAF"
}'
```
   which returns a job identifier.
```json
{"msg":"job executed successfully","id":"nornir-sh-ip-int-8s578"}
```
5. Read the job output.
```console
curl -b ./token.txt -GET $KRITEN_URL'/api/v1/jobs/nornir-sh-ip-int-8s578/log' \
--header 'Content-Type: application/json'
```
  which returns the log.
  
```console
## init container logs
Cloning into '.'...
From https://github.com/kriten-io/kriten-community-toolkit.git
f10dfdeb8deb6a2f8ae01dea8ecfc9af1f8aeac0	HEAD
f10dfdeb8deb6a2f8ae01dea8ecfc9af1f8aeac0	refs/heads/main


##application container logs 
netmiko_send_command************************************************************
* LF01 ** changed : False ******************************************************
vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
                                                                                    Address
Interface          IP Address               Status       Protocol            MTU    Owner  
------------------ ------------------------ ------------ -------------- ----------- -------
Ethernet49/1       10.255.255.1/31          up           up                 1500           
Ethernet50/1       10.255.255.3/31          up           up                 1500           
Loopback0          10.255.0.3/32            up           up                65535           
Loopback1          10.255.1.3/32            up           up                65535           
Management1        192.168.104.110/24       up           up                 1500           
Vlan123            192.168.3.253/23         up           up                 1500           
Vlan1195           unassigned               up           up                 9344           

^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* LF02 ** changed : False ******************************************************
vvvv netmiko_send_command ** changed : False vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
                                                                                    Address
Interface          IP Address               Status       Protocol            MTU    Owner  
------------------ ------------------------ ------------ -------------- ----------- -------
Ethernet37         172.16.2.1/24            up           up                 1500           
Ethernet41         172.16.1.1/24            up           up                 1500           
Ethernet49/1       10.255.255.5/31          up           up                 1500           
Ethernet50/1       10.255.255.7/31          up           up                 1500           
Loopback0          10.255.0.4/32            up           up                65535           
Loopback1          10.255.1.4/32            up           up                65535           
Management1        192.168.104.155/24       up           up                 1500           
Vlan123            192.168.3.253/23         up           up                 1500           
Vlan1195           unassigned               up           up                 9344           

^^^^ END netmiko_send_command ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```
