import os
import requests
import sys
import json
import urllib3

#urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#urllib3.disable_warnings(urllib3.exceptions.InsecurePlatformWarning)
#urllib3.disable_warnings(urllib3.exceptions.SNIMissingWarning)

extra_vars = json.loads(os.environ.get("EXTRA_VARS"))
slack_url = os.environ.get("SLACK_URL")

msg = extra_vars['msg']

data = {'text': msg }

slack_url = slack_url

response = requests.post(slack_url, data=json.dumps(data), verify=False)

response = {"response_code": response.status_code}

print('^JSON\n')
print(json.dumps(response))
print('^JSON\n')

print('\n')
print('Script completed.')
