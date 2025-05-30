#!/usr/bin/env python
import json
import os
import ssl

from nornir import InitNornir
from nornir.core.inventory import Host
from nornir_infrahub.plugins.tasks import get_artifact
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_configure
from napalm import get_network_driver

def filter_by_infrahub_node_id(host: Host, node_id: str) -> bool:
    node = host.get("InfrahubNode")
    if not node:
        raise ValueError(f"Host {host.name} does not contain a valid InfrahubNode")
    if not hasattr(node, "id"):
        raise ValueError(f"InfrahubNode {node} does not have an id")
    return node.id == node_id
    
def main():
    # Data from the webhook is passed in the EXTRA_VARS environment variable
    extra_vars = os.getenv("EXTRA_VARS")
    print("Extra Vars: ", extra_vars)
    extra_vars = json.loads(extra_vars)
    # The secrets are passed to the container from the Kriten runner
    token = os.getenv("INFRAHUB_API_TOKEN")
    infrahub_url = os.getenv("INFRAHUB_URL")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    # Set node_id and artifact_id  
    data = extra_vars.get("data", {})
    node_id = data.get("target_id")
    artifact_id = data.get("node_id")
    # Both node_id and artifact_id are needed
    if not node_id:
        raise RuntimeError(f"There is no target_id provided in extra_vars")

    if not artifact_id:
        raise RuntimeError(f"There is no artifact_id provided in extra_vars")
    # Use the Nornir Infrahub plugin to collect device inventory
    nr = InitNornir(
        inventory={
            "plugin": "InfrahubInventory",
            "options": {
                "address": infrahub_url,
                "token": token,
                "host_node": {"kind": "InfraDevice"},
                "schema_mappings": [
                    {"name": "hostname", "mapping": "primary_address.address"},
                    {"name": "platform", "mapping": "platform.nornir_platform"},
                ]
            },
        }
    )
    # Set Nornir variables for switch username and password
    nr.inventory.defaults.username = username
    nr.inventory.defaults.password = password
    # Filter the inventory to find the device which has updated 
    nr = nr.filter(filter_func=filter_by_infrahub_node_id, node_id=node_id)
    # Extract the device name
    name = list(nr.inventory.hosts.keys())[0]
    host = nr.inventory.hosts[name]
    # Get the startup-config artifact
    result = nr.run(task=get_artifact, artifact_id=artifact_id)
    config = str(result[name][0])
    # Set TLS args
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    #context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    # Using the EOS default ciphers
    context.set_ciphers('AES256-SHA:DHE-RSA-AES256-SHA:AES128-SHA:DHE-RSA-AES128-SHA')
    # Use Nornir NAPALM to configure the switch
    result = nr.run(task=napalm_configure, configuration=config, dry_run=False)
    print_result(result)
    
if __name__ == "__main__":
    main()
