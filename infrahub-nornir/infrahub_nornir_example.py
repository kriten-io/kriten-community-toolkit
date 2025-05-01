#!/usr/bin/env python
import json
import os

from nornir import InitNornir
from nornir.core.inventory import Host
from nornir_infrahub.plugins.tasks import get_artifact
from nornir_utils.plugins.functions import print_result
from nornir_napalm.plugins.tasks import napalm_configure


def filter_by_infrahub_node_id(host: Host, node_id: str) -> bool:
    node = host.get("InfrahubNode")
    if not node:
        raise ValueError(f"Host {host.name} does not contain a valid InfrahubNode")


    if not hasattr(node, "id"):
        raise ValueError(f"InfrahubNode {node} does not have an id")

    return node.id == node_id

    
def main():
    extra_vars = os.getenv("EXTRA_VARS")
    print("Extra Vars: ", extra_vars)
    extra_vars = json.loads(extra_vars)
    token = os.getenv("INFRAHUB_API_TOKEN")
  
    data = extra_vars.get("data", {})
    node_id = data.get("target_id")
    artifact_id = data.get("node_id")

    if not node_id:
        raise RuntimeError(f"There is no target_id provided in extra_vars")

    if not artifact_id:
        raise RuntimeError(f"There is no artifact_id provided in extra_vars")

    nr = InitNornir(
        inventory={
            "plugin": "InfrahubInventory",
            "options": {
                "address": "http://192.168.10.57:8000",
                "token": token,
                "host_node": {"kind": "InfraDevice"},
                "schema_mappings": [
                    {"name": "hostname", "mapping": "primary_address.address"},
                    {"name": "platform", "mapping": "platform.nornir_platform"},
                ]
            },
        }
    )

    nr = nr.filter(filter_func=filter_by_infrahub_node_id, node_id=node_id)

    name = list(nr.inventory.hosts.keys())[0]
    host = nr.inventory.hosts[name]
    result = nr.run(task=get_artifact, artifact_id=artifact_id)
    config = result[name][0].split("\n")

    result = nr.run(task=napalm_configure, configuration=config, dry_run=False)
    print_result(result)

        
    
if __name__ == "__main__":
    main()
