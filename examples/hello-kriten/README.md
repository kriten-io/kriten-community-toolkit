# hello-kriten

There is a simple python script, which demonstrates access to input variables and secrets, provided by Kriten to the Job container, where the script is executed.

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
  "name": "python-3.9",
  "image": "python:3.9-slim",
  "gitURL": "https://github.com/kriten-io/kriten-community-toolkit.git",
  "branch": "main",
  "secret": {
      "username": "admin",
      "password": "P@55w0rd!",
      "super_secret": "1234567890!"
  }
}'
```
3. Create a task that references the runner and the command to run the script.
```console
curl -b ./token.txt -X POST $KRITEN_URL'/api/v1/tasks' \
--header 'Content-Type: application/json' \
--data '{
  "name": "hello-kriten",
  "command": "python examples/hello-kriten/hello-kriten.py",
  "runner": "python-3.9"
}'
```
4. Launch job.
```console
curl -b ./token.txt -X POST $KRITEN_URL'/api/v1/jobs/hello-kriten' \
--header 'Content-Type: application/json' \
--data '{
  "agent_name": "Ethan Hunt",
  "operation":"Mission impossible"
}'
```
   which returns a job identifier.
```json
{"msg":"job executed successfully","value":"hello-kriten-ks67g"}
```
5. Read the job output.
```console
curl -b ./token.txt -X GET $KRITEN_URL'/api/v1/jobs/hello-kriten-ks67g' \
--header 'Content-Type: application/json'
```
   which returns a message.
```json
{
  "id": "hello-kriten-ks67g",
  "owner": "root",
  "startTime": "Fri Dec 15 17:11:35 UTC 2023",
  "completionTime": "Fri Dec 15 17:11:40 UTC 2023",
  "failed": 0,
  "completed": 1,
  "stdout": "Hello, Kriten!\n\nThis script demonstrates Kriten's capabilities.\nIt reads input variables (EXTRA_VARS) and secrets, and prints them.\n\n\n^JSON\n\n{\"extra_vars\": {\"agent_name\": \"Ethan Hunt\", \"operation\": \"Mission impossible\"}, \"secrets\": {\"password\": \"P@55w0rd!\", \"username\": \"admin\", \"super_secret\": \"1234567890!\"}}\n^JSON\n\n\n\nScript completed.\n",
  "json_data": {
    "extra_vars": {
      "agent_name": "Ethan Hunt",
      "operation": "Mission impossible"
    },
    "secrets": {
      "password": "P@55w0rd!",
      "super_secret": "1234567890!",
      "username": "admin"
    }
  }
}

```

  To return job stdout as text, append /log to the URL
```console
curl -b ./token.txt -GET $KRITEN_URL'/api/v1/jobs/hello-kriten-ks67g/log' \
--header 'Content-Type: application/json'
```
  which returns a message.
  
```console
Hello, Kriten!

This script demonstrates Kriten's capabilities.
It reads input variables (EXTRA_VARS) and secrets, and prints them.


^JSON

{"extra_vars": {"agent_name": "Ethan Hunt", "operation": "Mission impossible"}, "secrets": {"password": "P@55w0rd!", "username": "admin", "super_secret": "1234567890!"}}
^JSON



Script completed.
```
