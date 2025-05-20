Login:
```
curl -c ./token.txt -X POST $KRITEN_URL'/api/v1/login' \
--header 'Content-Type: application/json' \
--data '{
  "username": "root",
  "password": "root",
  "provider": "local"
}' 
```

Create the runner:
```
curl -b ./token.txt -X POST $KRITEN_URL'/api/v1/runners' \
--header 'Content-Type: application/json' \
--data '{
  "name": "ansible",
  "image": "kubecodeio/kriten-ansible:0.1",
  "gitURL": "https://github.com/kriten-io/kriten-community-toolkit.git",
  "branch": "main",
  "secret": {
      "github_pat": "<PERSONAL_ACCESS_TOKEN",
      "github_userid": "beertwanger",
      "github_username": "Steve Corp",
      "github_email": "steve@kubecode.io",
      "github_repo": "https://github.com/kriten-io/network-backups-demo",
      "network_username": "admin",
      "network_password": "admin"
  }
}'
```

Create the task
```

curl -b ./token.txt -X POST $KRITEN_URL'/api/v1/tasks' \
--header 'Content-Type: application/json' \
--data '{
  "name": "network-backup",
  "command": "cd ansible/network_backup/; ansible-playbook -i hosts.yml network_backup.yml",
  "runner": "ansible",
  "schema":
    {
      "additionalProperties": false,
      "description": "Backup network device config.",
      "properties": {
        "target_hosts": {
          "minLength": 1,
          "type": "string"
        }
      },
      "required": [
        "target_hosts"
      ]
    }
}'
```
