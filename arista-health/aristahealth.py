#!/usr/bin/env python3
"""Collect health information from Arista EOS switches.

Credentials and inventory come from environment variables:
  ARISTA_USERNAME    - login user for the switches
  ARISTA_PASSWORD    - login password for the switches
  INVENTORY_SOURCE - CVP or INFRAHUB
  CVP_URL     - Arista CVP host or URL, e.g. www.arista.io
  CVP_TOKEN   - Arista CVP API token, sent as a Bearer token
  INFRAHUB_ADDRESS -  "http://192.168.10.59:8000"
  INFRAHUB_API_TOKEN - "06438eb2-8019-4776-878c-0941b1f1d1ec"

The inventory is pulled from CVP or INFRAHUB as [{"device": fqdn, "ip": ip_address}, ...].
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime

import os
from infrahub_sdk import Config, InfrahubClientSync

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {'Accept': 'application/json', 'Content-Type': 'application/json'}
REQUEST_TIMEOUT = 10
TOP_MEMORY_RE = re.compile(r'([\d.]+)\s+(total|free|used|buff/cache|buffers|cached)')


class Arista:

    def __init__(self, username, password, inventory, logger=None, debug=False):
        self.username = username
        self.password = password
        self.inventory = inventory
        self.debug = debug
        self.logger = logger or logging.getLogger(__name__)
        self.docs = {'health': [], 'unreachable': []}

    # ------------------------------------------------------------------
    # Collection loop
    # ------------------------------------------------------------------

    def collect_data(self):
        collectors = [
            ('system', self._proc_cpu),
            ('power_supplies', self._env_power),
            ('cooling', self._env_cooling),
            ('temperature', self._env_temperature),
            ('lldp_neighbors', self._lldp_neighbors),
            ('last_reload', self._reload_cause),
            ('tacacs', self._tacacs_status),
            ('snmp', self._snmp_status),
            ('interfaces', self._interfaces_status),
            ('discards', self._interfaces_discards),
            ('bgp', self._bgp_summary),
            ('routes', self._ip_route_summary),
            ('port_channel', self._port_channel),
            ('mlag_detail', self._mlag_detail),
            ('virtual_router', self._virtual_router),
        ]

        for entry in self.inventory:
            device = entry['device']
            host = entry['ip']
            doc = {'device': device}
            session = requests.Session()
            try:
                response = session.post('https://{}/login'.format(host), data=json.dumps(
                    {'username': self.username, 'password': self.password}),
                    headers=HEADERS, timeout=REQUEST_TIMEOUT, verify=False)
                if response.status_code != 200:
                    self._mark_unreachable(device, 'API error {}'.format(response.status_code))
                    continue

                for key, collector in collectors:
                    try:
                        doc[key] = collector(session, host)
                    except Exception as error:
                        self._warn('{} collection failed for {}: {}'.format(key, device, error))

                self.docs['health'].append(doc)
                self._info('Data collected from device {}.'.format(device))
                self._logout(session, host)
            except Exception as error:
                self._mark_unreachable(device, str(error))
            finally:
                session.close()

    def _logout(self, session, host):
        try:
            session.post('https://{}/logout'.format(host), data=json.dumps(
                {'username': self.username, 'password': self.password}),
                headers=HEADERS, timeout=REQUEST_TIMEOUT, verify=False)
        except Exception as error:
            self._warn('Logout failed for {}: {}'.format(host, error))

    def _mark_unreachable(self, device, reason):
        self.docs['unreachable'].append({'device': device})
        self._warn('{} unreachable: {}'.format(device, reason))

    def _info(self, msg):
        self.logger.info(msg)

    def _warn(self, msg):
        self.logger.warning(msg)

    # ------------------------------------------------------------------
    # eAPI helper
    # ------------------------------------------------------------------

    def _run_command(self, session, host, command, fmt='json'):
        payload = {
            'jsonrpc': '2.0',
            'method': 'runCmds',
            'id': '1',
            'params': {'version': 1, 'cmds': [command], 'format': fmt},
        }
        response = session.post('https://{}/command-api'.format(host), data=json.dumps(payload),
                                headers=HEADERS, timeout=REQUEST_TIMEOUT, verify=False)
        if response.status_code != 200:
            raise RuntimeError('{} failed, HTTP {}'.format(command, response.status_code))
        body = response.json()
        if 'error' in body:
            raise RuntimeError('{} failed: {}'.format(command, body['error'].get('message', body['error'])))
        return body['result'][0]

    # ------------------------------------------------------------------
    # Collectors. Each returns the data for its document key, or raises.
    # ------------------------------------------------------------------

    def _proc_cpu(self, session, host):
        output = self._run_command(session, host, 'show processes top once', fmt='text')['output']
        data = {}
        for line in output.splitlines():
            if 'load average:' in line:
                load = re.search(r'load average:\s*([\d.]+),\s*([\d.]+),\s*([\d.]+)', line)
                if load:
                    data['one_min'], data['five_min'], data['fifteen_min'] = (float(v) for v in load.groups())
            elif line.startswith('KiB Mem'):
                mem = {label: float(value) for value, label in TOP_MEMORY_RE.findall(line)}
                total = mem.get('total', 0)
                if total:
                    buff_cache = mem.get('buff/cache', 0) + mem.get('buffers', 0) + mem.get('cached', 0)
                    used = mem.get('used', 0)
                    data['mem_utilization'] = round((used - buff_cache) / total * 100, 2)
        return data

    def _env_power(self, session, host):
        supplies = self._run_command(session, host, 'show environment power')['powerSupplies']
        return {slot: {'state': ps['state']} for slot, ps in supplies.items()}

    def _env_cooling(self, session, host):
        result = self._run_command(session, host, 'show system environment cooling')
        data = {
            'status': result['systemStatus'],
            'ambientTemperature': result['ambientTemperature'],
            'fanStatus': result['fansStatus']
        }
        for tray in result.get('fanTraySlots', []):
            if tray['fans']:
                data['fanTray' + tray['fans'][0]['label']] = tray['fans'][0]['actualSpeed']
        for psu in result.get('powerSupplySlots', []):
            if psu['fans'] and psu['status'] == "ok":
                data[psu['fans'][0]['label']] = psu['fans'][0]['actualSpeed']
        return data

    def _env_temperature(self, session, host):
        result = self._run_command(session, host, 'show system environment temperature')
        return {
            'status': result['systemStatus'],
            'alert_count': sum(sensor['alertCount'] for sensor in result.get('tempSensors', [])),
        }

    def _lldp_neighbors(self, session, host):
        result = self._run_command(session, host, 'show lldp neighbors')
        return len(result['lldpNeighbors'])

    def _reload_cause(self, session, host):
        causes = self._run_command(session, host, 'show reload cause full')['resetCauses']
        last = causes[-1]
        elapsed = datetime.now() - datetime.fromtimestamp(last['timestamp'])
        return {'cause': last['description'], 'days_since': elapsed.days}

    def _tacacs_status(self, session, host):
        output = self._run_command(session, host, 'show tacacs', fmt='text')['output']
        data = {'failures': 0, 'timeouts': 0}
        for line in output.splitlines():
            if 'Connection failures' in line:
                data['failures'] = int(line.split(':', 1)[1])
            elif 'Connection timeouts' in line:
                data['timeouts'] = int(line.split(':', 1)[1])
        return data

    def _snmp_status(self, session, host):
        output = self._run_command(session, host, 'show snmp', fmt='text')['output']
        status = ''
        servers = 0
        for line in output.splitlines():
            if 'SNMP logging' in line:
                status = line.split(':', 1)[1].strip()
            if 'Logging to' in line:
                servers += 1
        return {'status': status, 'servers': servers}

    def _interfaces_status(self, session, host):
        statuses = self._run_command(session, host, 'show interfaces status')['interfaceStatuses']
        data = {'up': 0, 'down': 0, 'disabled': 0, 'err-disabled': 0}
        for info in statuses.values():
            link = info['linkStatus']
            if link == 'connected':
                data['up'] += 1
            elif link == 'notconnect':
                data['down'] += 1
            elif link == 'disabled':
                data['disabled'] += 1
            elif 'err' in link:
                data['err-disabled'] += 1
        return data

    def _interfaces_discards(self, session, host):
        result = self._run_command(session, host, 'show interfaces counters discards')
        return {'in': result['inDiscardsTotal'], 'out': result['outDiscardsTotal']}

    def _bgp_summary(self, session, host):
        vrfs = self._run_command(session, host, 'show ip bgp summary vrf all')['vrfs']
        data = {}
        peers = 0
        for vrf, vrf_info in vrfs.items():
            for peer, peer_info in (vrf_info.get('peers') or {}).items():
                peers += 1
                if peer_info['peerState'] != 'Established':
                    data['vrf'] = vrf
                    data['peer'] = peer
                    data['peer_status'] = peer_info['peerState']
        data['peers'] = peers
        return data

    def _ip_route_summary(self, session, host):
        summary = self._run_command(session, host, 'show ip route summary')
        bgp_total = summary.get('bgpCounts', {}).get('bgpTotal', 0)
        static = summary['static']
        connected = summary['connected']
        return {
            'total': bgp_total + static + connected,
            'bgp_total': bgp_total,
            'connected': connected,
            'static': static,
        }

    def _port_channel(self, session, host):
        channels = self._run_command(session, host, 'show port-channel all-ports')['portChannels']
        data = {'inactive_ports': 0}
        for pc, pc_info in channels.items():
            if pc_info['inactivePorts']:
                data[pc] = pc_info['inactivePorts']
                data['inactive_ports'] += len(pc_info['inactivePorts'])
        return data

    def _mlag_detail(self, session, host):
        mlag = self._run_command(session, host, 'show mlag detail')
        if not mlag['detail']['enabled']:
            return {}
        interfaces = self._run_command(session, host, 'show mlag interfaces')['interfaces'] or {}
        data = {
            'mlag_enabled': True,
            'mlag_state': mlag['state'],
            'mlag_role': mlag['detail']['mlagState'],
            'mlag_config_sanity': mlag.get('configSanity', 'unknown'),
            'mlag_ports': mlag['mlagPorts'],
        }
        for info in interfaces.values():
            if info['status'] != 'active-full':
                data[info['localInterface']] = {'status': info['status']}
        return data

    def _virtual_router(self, session, host):
        routers = self._run_command(session, host, 'show ip virtual-router')['virtualRouters'] or []
        return {vr['interface']: vr['protocolStatus'] for vr in routers}


def get_inventory():
    # Default INFRAHUB_API_TOKEN: "06438eb2-8019-4776-878c-0941b1f1d1ec"
    address=os.getenv("INFRAHUB_ADDRESS", "http://192.168.10.59:8000")
    api_token=os.getenv("INFRAHUB_API_TOKEN", "06438eb2-8019-4776-878c-0941b1f1d1ec")
    if not address or not api_token:
        sys.exit('ERROR: INFRAHUB_ADDRESS and INFRAHUB_API_TOKEN environment variables must be set.')
    config = Config(
        address=address,
        api_token=api_token
    )
    client = InfrahubClientSync(config=config)
    # Retrieve all devices (change kind to "DcimDevice" if using the DCIM schema)
    # prefetch_relationships=True loads cardinality-one peers (e.g., site, platform)
    kind="AvdLeafswitch"
    devices = client.all(kind=kind, prefetch_relationships=True)
    inventory = []
    for device in devices:
        name = device.name.value
        primary_address = str(device.primary_address.peer.address.value)
        ip = primary_address.split("/")[0]
        inventory.append({"device": name, "ip": ip})
    if not inventory:
        sys.exit(f'ERROR: No devices of kind {kind} found in Infrahub inventory.')
    print(f"Infrahub inventory from {address}")
    return inventory

def get_cvp_inventory():
    cvp_url = os.environ.get('CVP_URL')
    token = os.environ.get('CVP_TOKEN')
    if not cvp_url or not token:
        sys.exit('ERROR: CVP_URL and CVP_TOKEN environment variables must be set.')
    base = cvp_url if cvp_url.startswith('http') else 'https://{}'.format(cvp_url)
    headers = dict(HEADERS, Authorization='Bearer {}'.format(token))
    try:
        response = requests.get(base.rstrip('/') + '/cvpservice/inventory/devices', headers=headers,
                                timeout=REQUEST_TIMEOUT, verify=False)
    except requests.RequestException as error:
        sys.exit('ERROR: Unable to reach CVP: {}'.format(error))
    if response.status_code != 200:
        sys.exit('ERROR: CVP inventory request failed, HTTP {}'.format(response.status_code))
    inventory = [{'device': device['fqdn'], 'ip': device['ipAddress']}
                 for device in response.json() if device.get('fqdn') and device.get('ipAddress')]
    if not inventory:
        sys.exit('ERROR: No devices with fqdn and ipAddress found in CVP.')
    print(f"CVP inventory from {cvp_url}")
    return inventory

def get_credentials():
    username = os.environ.get('ARISTA_USERNAME')
    password = os.environ.get('ARISTA_PASSWORD')
    if not username or not password:
        sys.exit('ERROR: USERNAME and PASSWORD environment variables must be set.')
    return username, password


def setup_logging(debug):
    logger = logging.getLogger('aristabeat')
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(handler)
    return logger


def parse_args():
    parser = argparse.ArgumentParser(description='Collect health data from Arista switches.')
    parser.add_argument('-d', '--debug', action='store_true', help='enable debug output')
    return parser.parse_args()


def main():
    inventory_source = os.getenv("INVENTORY_SOURCE", "CVP")
    args = parse_args()
    username, password = get_credentials()
    match inventory_source:
        case "CVP":
            inventory = get_cvp_inventory()
        case "INFRAHUB":
            inventory = get_inventory()
    logger = setup_logging(args.debug)
    beat = Arista(username, password, inventory, logger=logger, debug=args.debug)
    beat.collect_data()
    print("^JSON\n")
    print(json.dumps(beat.docs, indent=2))
    print("^JSON\n")


if __name__ == '__main__':
    main()
