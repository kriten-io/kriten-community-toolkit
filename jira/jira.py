import json
import os
import requests
from requests.auth import HTTPBasicAuth
import sys

# 1. Configuration & Authentication

extra_vars = os.environ.get('EXTRA_VARS')

if extra_vars:
    extra_vars_data = json.loads(extra_vars)
else:
    sys.exit()

JIRA_INSTANCE = extra_vars_data["JIRA_INSTANCE"]
EMAIL = extra_vars_data["EMAIL"]
API_TOKEN = extra_vars_data["API_TOKEN"]


URL = f"https://{JIRA_INSTANCE}/rest/servicedeskapi/request"

auth = HTTPBasicAuth(EMAIL, API_TOKEN)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# 2. Define Request Payload
# You must supply your Service Desk ID and Request Type ID.
payload = {
    "serviceDeskId": "1",        # Numeric ID of your Service Desk portal
    "requestTypeId": "1",      # Numeric ID of the specific Request Type
    "requestFieldValues": {
        "summary": "Access issue with production database",
        "description": "Unable to connect to the DB using the standard service account credentials."
    },
    # Optional fields (Requires specific agent/admin permissions):
    # "raiseOnBehalfOf": "customer-account-id", 
    # "requestParticipants": ["participant-account-id"]
}

# 3. Send the Request
try:
    response = requests.post(URL, data=json.dumps(payload), headers=headers, auth=auth)
    response.raise_for_status()  # Check for HTTP errors
    
    # Success response code is 201 Created
    request_data = response.json()
    print("Successfully raised request!")
    print(f"Request Key: {request_data.get('issueKey')}")
    print(f"Request ID: {request_data.get('issueId')}")

except requests.exceptions.HTTPError as err:
    print(f"HTTP Error occurred: {err}")
    print(f"Response details: {response.text}") # Helps debug missing mandatory fields

