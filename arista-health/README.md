
# Collect health information from Arista EOS switches.

## aristahealth.py

Script pulls inventory from Cloud CVP (CVaaS) and pulls health information from Arista switches via eAPI

  Credentials and inventory come from environment variables:

    ```USERNAME```    - login user for the switches

    ```PASSWORD```    - login password for the switches

    ```CVP_URL```     - Arista CVP host or URL, e.g. www.arista.io

    ```CVP_TOKEN```   - Arista CVP API token, sent as a Bearer token

  The inventory is pulled from CVP as [{"device": fqdn, "ip": ip_address}, ...].


## aristahealth_nornir.py

Script pulls inventory from Infrahub SoT using nornir infrahub plugin and uses nornir to pull health information from Arista switches via eAPI

    ```USERNAME```    - login user for the switches

    ```PASSWORD```    - login password for the switches

    ```INFRAHUB_URL```     - Infrahub URL, i.e. http://192.168.100.100:8000

    ```INFRAHUB_TOKEN```   - Infrahub Token