from nornir import InitNornir
from nornir.core.plugins.inventory import InventoryPluginRegister
from nornir_infrahub.plugins.inventory.infrahub import InfrahubInventory

def main():
    # Register the custom InfrahubInventory plugin
    InventoryPluginRegister.register("InfrahubInventory", InfrahubInventory)

    # Initialize Nornir with InfrahubInventory as the inventory plugin
    nr = InitNornir(
        inventory={
            "plugin": "InfrahubInventory",
            "options": {
                "address": "http://192.168.10.59:8000",  # Infrahub API URL
                "token": "1838a9d1-21e5-686c-3967-c51ef722c266",  # Infrahub API token
                "host_node": {"kind": "InfraDevice"},  # Infrahub Node kind to map to Nornir Hosts
                "schema_mappings": [
                    {"name": "hostname", "mapping": "primary_address.address"},
                    {"name": "platform", "mapping": "platform.nornir_platform"},
                ],  # Mapping Nornir Host properties to Infrahub Node attributes
                "group_mappings": ["site.name"],  # Create Nornir groups from Infrahub Node attributes
                "group_file": "dummy.yml",  # Path to the group file
            },
        }
    )

    # Print Nornir inventory host and group names
    print(nr.inventory.hosts.keys())
    print(nr.inventory.groups.keys())

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
