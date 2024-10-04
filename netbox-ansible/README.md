# netbox-ansible

Ansible playbooks that read the inventory from NetBox and connect to network devices.
These playbooks have been adapted from [netbox-learning](https://github.com/netboxlabs/netbox-learning) repository.

## To run on Kriten:

Where $KRITEN_URL is set to the URL of your Kriten instance.
eg. `export KRITEN_URL=http://kriten-community.kriten.io`

1. Login
```
curl -c ./token.txt $KRITEN_URL'/api/v1/login' \
--header 'Content-Type: application/json' \
--data '{
  "username": "root",
  "password": "root",
  "provider": "local"
}' 
```
2. Create a runner which references an image with Ansible installed.
```
curl -b ./token.txt $KRITEN_URL'/api/v1/runners' \
--header 'Content-Type: application/json' \
--data '{
  "branch": "main",
  "name": "netbox-ansible",
  "image": "evolvere/netbox-ansible-webinar:0.1",
  "gitURL": "https://github.com/kriten-io/kriten-examples.git"
}'
```
3. Create a task that references the runner and the command to run the script.
```
curl -b ./token.txt $KRITEN_URL'/api/v1/tasks' \
--header 'Content-Type: application/json' \
--data '{
  "name": "netbox-ansible-compare-configs",
  "command": "ansible-playbook -i netbox-ansible/netbox_inv.yml netbox-ansible/compare_intended_vs_actual.yml",
  "runner": "netbox-ansible",
  "secret": {
      "NETBOX_TOKEN": "a08684c4649c091e201f1eeb4eb5c18531e6d1b3",
      "NETBOX_API": "http://192.168.10.55:8000/"
  },
      "schema": {
              "properties": {
                  "target_hosts": {
                      "type": "string",
                      "pattern": "^[A-Za-z0-9-]+$",
                      "minLength": 1
                  }
                  },
                  "required": [
                      "target_hosts"
                  ],
                  "additionalProperties": false
              }
          }

}'
```
4. Launch job.
```
curl -b ./token.txt $KRITEN_URL'/api/v1/jobs/netbox-ansible-compare-configs' \
--header 'Content-Type: application/json' \
--data '{
  "target_hosts": "all"
}'
```
   which returns a job identifier.
```
{"msg":"job created successfully","id":"netbox-ansible-compare-configs-6cx4"}
```
5. Read the job's stdout output.
```
curl -b ./token.txt $KRITEN_URL'/api/v1/jobs/netbox-ansible-compare-configs-6cx4/log' \
--header 'Content-Type: application/json'
```
   which returns the ansible output.

## To run from NetBox

Add the Python scripts from custom_scripts to NetBox using the Customization > Scripts menu.

