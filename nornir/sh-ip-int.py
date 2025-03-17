import json
import os
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko import netmiko_send_command
from nornir.core.filter import F

extra_vars = os.environ.get('EXTRA_VARS')

nr = InitNornir(config_file="./config.yml")

if extra_vars:
    extra_vars_data = json.loads(extra_vars)
    group = extra_vars_data["group"]
    switch_group = nr.filter(F(groups__contains=group))
    result = switch_group.run(netmiko_send_command, command_string="sh ip int brief")
else:
    result = nr.run(netmiko_send_command, command_string="sh ip int brief")
    
print_result(result)
