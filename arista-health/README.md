#Collect health information from Arista EOS switches.

Credentials and inventory come from environment variables:

  ```ARISTA_USERNAME```    - login user for the switches

  ```ARISTA_PASSWORD```    - login password for the switches

  ```INVENTORY_SOURCE```   - CVP or INFRAHUB

  ```CVP_URL```            - Arista CVP host or URL, e.g. www.arista.io

  ```CVP_TOKEN```          - Arista CVP API token, sent as a Bearer token

  ```INFRAHUB_ADDRESS```   - Infrahub address, e.g. "http://192.168.10.59:8000"

  ```INFRAHUB_API_TOKEN``` - Infrahub API token, e.g. "06438eb2-8019-4776-878c-0941b1f1d1ec"

The inventory is pulled from CVP and INFRAHUB as [{"device": fqdn, "ip": ip_address}, ...].


