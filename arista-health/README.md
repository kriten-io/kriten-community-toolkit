#Collect health information from Arista EOS switches.

Credentials and inventory come from environment variables:

  ```USERNAME```    - login user for the switches

  ```PASSWORD```    - login password for the switches

  ```CVP_URL```     - Arista CVP host or URL, e.g. www.arista.io

  ```CVP_TOKEN```   - Arista CVP API token, sent as a Bearer token

The inventory is pulled from CVP as [{"device": fqdn, "ip": ip_address}, ...].


