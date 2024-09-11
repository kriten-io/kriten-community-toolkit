# xmas

A seasonal greeting

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
  "name": "kriten-xmas-example",
  "image": "kubecodeio/kriten-xmas:0.1",
  'branch": "main",
  "gitURL": "https://github.com/kriten-io/kriten-community-toolkit.git"
}'
```
3. Create a task that references the runner and the command to run the script.
```console
curl -b ./token.txt -X POST $KRITEN_URL'/api/v1/tasks' \
--header 'Content-Type: application/json' \
--data '{
      "name": "merry-xmas",
      "command": "python examples/xmas/xmas.py",
      "runner": "kriten-xmas-example",
        "schema": {
          "required": [
            "from"
          ],
          "properties": {
            "from": {
              "type": "string", 
                "pattern": "^[A-Za-z0-9-]+$",
                  "minLength": 1
              }
          },
          "additionalProperties": false
        }
      "synchronous": true
    }'
```
4. Launch job.
```console
curl -b ./token.txt -X POST $KRITEN_URL'/api/v1/jobs/merry-xmas' \
--header 'Content-Type: application/json' \
--data '{
  "from": "Steve"
}'
```
   which returns a job identifier.
```json
{"id":"xmas-dx982", "msg":"job created successfully"}
```
5. Read the job output.
```console
curl -b ./token.txt -X GET $KRITEN_URL'/api/v1/jobs/xmas-dx982/log' \
--header 'Content-Type: application/json'
```
   which returns a message.
```console
 __  __                         ____ _          _     _                       
|  \/  | ___ _ __ _ __ _   _   / ___| |__  _ __(_)___| |_ _ __ ___   __ _ ___ 
| |\/| |/ _ \ '__| '__| | | | | |   | '_ \| '__| / __| __| '_ ` _ \ / _` / __|
| |  | |  __/ |  | |  | |_| | | |___| | | | |  | \__ \ |_| | | | | | (_| \__ \
|_|  |_|\___|_|  |_|   \__, |  \____|_| |_|_|  |_|___/\__|_| |_| |_|\__,_|___/
                       |___/                                                  

  __                       ____  _                 
 / _|_ __ ___  _ __ ___   / ___|| |_ _____   _____ 
| |_| '__/ _ \| '_ ` _ \  \___ \| __/ _ \ \ / / _ \
|  _| | | (_) | | | | | |  ___) | ||  __/\ V /  __/
|_| |_|  \___/|_| |_| |_| |____/ \__\___| \_/ \___|
```
