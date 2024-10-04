from django.utils.text import slugify
from django.forms import PasswordInput

from dcim.choices import DeviceStatusChoices, SiteStatusChoices
from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from extras.scripts import *

import time
import requests
import json


class CNFCMPY(Script):

    class Meta:
        name = "Compare Configs"
        description = "Compare NetBox intended state with actual running config."
        commit_default = False
        field_order = ['kriten_url', 'kriten_username', 'kriten_password']

    kriten_url = StringVar(
        description="URL for Kriten task",
        default = "http://kriten.192.168.10.102.nip.io"
    )
    kriten_username = StringVar(
        description="Kriten username",
        default="root"
    )
    kriten_password = StringVar(
        widget=PasswordInput,
        description="Kriten password"
    )
    target_hosts = StringVar(
        description="Device name, group or all"
    )

    def run(self, data, commit):
        # Launch job
        session = requests.Session()
        headers = {
            "Content-Type": "application/json"
        }
        payload = json.dumps({
            "username": data["kriten_username"],
            "password": data["kriten_password"],
            "provider": "local"
        })
        body = json.dumps({
            "target_hosts": data["target_hosts"]
        })
        login_url = f"{data['kriten_url']}/api/v1/login"

        launch_url = f"{data['kriten_url']}/api/v1/jobs/netbox-ansible-compare-configs"

        login = session.post(login_url, headers=headers, data=payload)
        stdout = ''
        if login.status_code == 200:
            launch = session.post(launch_url, headers=headers, data=body)
            if launch.status_code == 200:
                job_id = launch.json()["id"]
                self.log_success(f"Job {job_id} launched")
                job_not_finished = True
                result_url = f"{data['kriten_url']}/api/v1/jobs/{job_id}/log"
                while job_not_finished:
                    time.sleep(5)
                    result = session.get(result_url, headers=headers)
                    stdout = result.text
                    if "ignored=" in stdout:
                        job_not_finished = False
            else:
                self.log_failure(f"Kriten job launch failed")
        else:
            self.log_failure(f"Kriten job login failed")

        return stdout
