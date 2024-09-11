# Copyright: (c) 2023, vlad@evolvere-tech.co.uk
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: Cisco Aci scalability stats collector

short_description: Collector module for evobeat ansible collection.

version_added: "1.0.0"

description: Self contained Cisco ACI scalability stats collector developed to run with Ansible, result published to Elasticsearch using ansible evobeat.

options:
    hostname:
        description: Cisco APIC/Fabric name.
        required: true
        type: str
    
    hostip:
        description: IP address of Cisco ACI cluster.
        required: true
        type: str
        
    username:
        description: Username credential for Cisco ACI fabric.
        required: true
        type: str
        
    password:
        description: Password for Username credential for Cisco ACI fabric.
        required: true
        type: str
        no_log: True
        
author:
    - Vladimir Kupriyanov
'''

# Ansible required import
from ansible.module_utils.basic import AnsibleModule

# Custom Python Code starts Here
# >>>>

import datetime
import json
import sys
import requests
import urllib3

class Apic():
    # APIC login, connect and disconnect functions
    def __init__(self, **kwargs):
        self.version = '1.0.1'
        self.can_connect = ''
        self.fabric = []
        self.fabric_name = ''
        self.fabric_inventory = {}
        self.apic_address = None
        self.cookie = None
        self.headers = {'content-type': "application/json", 'cache-control': "no-cache"}
        self.epg_names = []
        self.idict = {}
        self.epgs = {}
        self.username = ''
        self.password = ''
        self.session = requests.Session()
        self.refresh_time_epoch = 0
        if kwargs:
            self.fabrics = kwargs['fabrics']
        #urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        #urllib3.disable_warnings(urllib3.exceptions.InsecurePlatformWarning)
        #urllib3.disable_warnings(urllib3.exceptions.SNIMissingWarning)

    def login(self, args):
        """Usage: login [FABRIC_NAME]"""
        msgs = []
        errors = []
        if self.can_connect:
            try:
                self.disconnect()
            except:
                pass
        self.can_connect = ''
        if len(args) == 0:
            msg = "Usage: login [FABRIC_NAME]"
            msgs.append(msg)
            return {'rc': 1, 'info': msgs}
        else:
            parameter_values = args.split()
            fabric_name = parameter_values[0]
            if fabric_name in self.fabrics.keys():
                self.fabric = self.fabrics[fabric_name]
                self.fabric_name = fabric_name
                for apic_credentials in self.fabric:
                    if not self.username or not self.password:
                        if not apic_credentials['username'] or not apic_credentials['password']:
                            msg = 'APIC username or password not supplied.'
                            errors.append(msg)
                            return {'rc': 1, 'error_msgs': errors}
                        else:
                            self.username = apic_credentials['username']
                            self.password = apic_credentials['password']

                    address = apic_credentials['address']
                    connection_result = self.connect(address=address, username=self.username, password=self.password)
                    if connection_result['rc'] == 0:
                        self.can_connect = parameter_values[0]
                        msg = 'Established connection to APIC in fabric', self.can_connect
                        msgs.append(msg)
                        return {'rc': 0, 'info': msgs}

                if not self.can_connect:
                    msg = 'Cannot connect to APIC in fabric {}'.format(fabric_name)
                    errors.append(msg)
                    return {'rc': 1, 'error_msgs': errors}

            msg = 'ERROR: Missing connection parameters for FABRIC {0}'.format(fabric_name)
            errors.append(msg)
            return {'rc': 1, 'error_msgs': errors}

    def connect(self, **kwargs):
        if kwargs:
            errors = []
            apic_user = kwargs['username']
            apic_password = kwargs['password']
            apic_address = kwargs['address']
            uri = "https://{0}/api/aaaLogin.json".format(apic_address)
            payload = {'aaaUser': {'attributes': {'name': apic_user, 'pwd': apic_password}}}
            try:
                response = self.session.post(uri, data=json.dumps(payload), headers=self.headers, verify=False,
                                            timeout=10)
                if response.status_code == 200:
                    self.cookie = {'APIC-cookie': response.cookies['APIC-cookie']}
                    self.apic_address = apic_address
                    self.refresh_time_epoch = int(datetime.datetime.now().strftime('%s'))
                    return {'rc': 0}
                else:
                    msg = 'ERROR: Failed to connect to APIC {0}, error code {1}'.format(apic_address,
                                                                                        response.status_code)
                    errors.append(msg)
                    return {'rc': 1, 'error_msgs': errors}
            except:
                msg = 'ERROR: Failed to connect to {}'.format(apic_address)
                errors.append(msg)
                return {'rc': 1, 'error_msgs': errors}
        else:
            pass

    def disconnect(self):
        try:
            self.session.close()
        except:
            pass

    def refresh_connection(self, timeout=90):
        errors = []
        try:
            current_time_epoch = int(datetime.datetime.now().strftime('%s'))

            if current_time_epoch - self.refresh_time_epoch >= timeout:
                apic_user = self.username
                apic_password = self.password
                apic_address = self.apic_address
                uri = "https://{0}/api/aaaLogin.json".format(apic_address)
                payload = {'aaaUser': {'attributes': {'name': apic_user, 'pwd': apic_password}}}
                response = self.session.post(uri, data=json.dumps(payload), headers=self.headers, verify=False)
                if response.status_code == 200:
                    self.cookie = {'APIC-cookie': response.cookies['APIC-cookie']}
                    self.apic_address = apic_address
                    self.refresh_time_epoch = int(datetime.datetime.now().strftime('%s'))
                else:
                    msg = 'No connection to Fabric {0}'.format(self.can_connect)
                    errors.append(msg)
                    self.can_connect = ''

        except Exception:
            msg = 'No connection to Fabric {0}'.format(self.can_connect)
            errors.append(msg)
            self.can_connect = ''

        if errors:
            return {'rc': 1, 'error_msgs': errors}
        else:
            return {'rc': 0}
    #
    # ACI Fabric functions
    #
    def aci_get_class(self, class_name, sub_classes=[]):
        # Refreshing connection to ACI
        f_name = sys._getframe().f_code.co_name
        result = self.refresh_connection()
        if result['rc'] == 1:
            return {'rc': 1, 'error_msgs': result['error_msgs']}
        if sub_classes:
            class_filter = ','.join(sub_classes)
            options = '?rsp-subtree=children&rsp-subtree-class={}'.format(class_filter)
        else:
            options = ''
        try:
            uri = "https://{0}/api/class/{1}.json".format(self.apic_address, class_name)
            if options:
                uri += options
            response = self.session.get(uri, headers=self.headers, cookies=self.cookie, verify=False).json()
            if response['imdata']:
                return {'rc': 0, 'data': response['imdata']}
            else:
                return {'rc': 1, 'data': [], 'error_msgs': [f'{f_name} - failed to query class object {class_name}']}
        except Exception as error:
            return {'rc': 1, 'error_msgs': [f'{f_name} - {str(error)}']}

    def aci_get_mo(self, dn, subtree_class):
        # Refreshing connection to ACI
        f_name = sys._getframe().f_code.co_name
        result = self.refresh_connection()
        if result['rc'] == 1:
            return {'rc': 1, 'error_msgs': result['error_msgs']}
        try:
            uri = "https://{0}/api/mo/{1}.json".format(self.apic_address, dn)
            subtree = 'children'
            options = '?rsp-subtree={}&rsp-subtree-class={}'.format(subtree, subtree_class)
            uri += options
            response = self.session.get(uri, headers=self.headers, cookies=self.cookie, verify=False).json()
            if response['imdata']:
                return {'rc': 0, 'data': response['imdata']}
            else:
                return {'rc': 1, 'data': [], 'error_msgs': [f'{f_name} - failed to query MO {dn}.']}
                
        except Exception as error:
            return {'rc': 1, 'error_msgs': [f'{f_name} - {str(error)}']}

    def aci_get_fabric_usage(self):
        f_name = sys._getframe().f_code.co_name
        docs = []
        result = self.refresh_connection()
        if result['rc'] == 1:
            return {'rc': 1, 'error_msgs': result['error_msgs']}
        try:
            # Collecting General Fabric Capacity info
            uri = "https://{0}/api/mo/uni/fabric/compcat-default/fvsw-default/capabilities.json".format(self.apic_address)
            options = '?query-target=children&target-subtree-class=fvcapRule'
            uri += options
            response = self.session.get(uri, headers=self.headers, cookies=self.cookie, verify=False).json()
            if not response['imdata']:
                return {'rc': 1, 'data': []}
            else:

                for limit_item in response['imdata']:
                    if limit_item.get('fvcapRule', ''):
                        limit_dict = limit_item['fvcapRule']['attributes']
                        if limit_dict['subj'] == 'fvTenant':
                            tn_max = int(limit_dict['constraint'])
                        elif limit_dict['subj'] == 'fvAEPg':
                            epg_max = int(limit_dict['constraint'])
                        elif limit_dict['subj'] == 'fvCEp':
                            ep_max = int(limit_dict['constraint'])
                        elif limit_dict['subj'] == 'fabricNodes':
                            fabric_nodes_max = int(limit_dict['constraint'])
                        elif limit_dict['subj'] == 'fvCtx':
                            vrf_max = int(limit_dict['constraint'])
                        elif limit_dict['subj'] == 'vzBrCP':
                            contracts_max = int(limit_dict['constraint'])
                        elif limit_dict['subj'] == 'fvBD':
                            bd_max = int(limit_dict['constraint'])
                
                docs.append({'evoaci.fabric_name': self.fabric_name,
                            'evoaci.doc_type': 'aci_fabric_capacity',
                            'evoaci.tn_max': tn_max,
                            'evoaci.epg_max': epg_max,
                            'evoaci.vrf_max': vrf_max,
                            'evoaci.contracts_max': contracts_max,
                            'evoaci.bd_max': bd_max})

            # Collecting TN info
            result = self.aci_get_class('fvTenant')
            tn_count = len(result['data'])

            # Collecting VRF info
            result = self.aci_get_class('fvCtx')
            vrf_count = len(result['data'])

            # Collecting Contracts info
            result = self.aci_get_class('vzBrCP')
            contracts_count = len(result['data'])

            # Collecting Contract Filters
            result = self.aci_get_class('vzFilter')
            contract_filters_count = len(result['data'])
            
            # Collecting BD info
            result = self.aci_get_class('fvBD')
            bd_count = len(result['data'])
        
            # Collecting EPG info
            result = self.aci_get_class('fvAEPg')
            epg_count = len(result['data'])

            docs.append({'evoaci.fabric_name': self.fabric_name,
                         'evoaci.doc_type': 'aci_fabric_usage',
                         'evoaci.tn_count': tn_count,
                         'evoaci.vrf_count': vrf_count,
                         'evoaci.contracts_count': contracts_count,
                         'evoaci.contact_filters_count': contract_filters_count,
                         'evoaci.bd_count': bd_count,
                         'evoaci.epg_count': epg_count})

            epgs_per_tenant = {}
            for item in result['data']:
                epg_info = item['fvAEPg']['attributes']
                epg_dn_split = epg_info['dn'].split('/')
                epg_name = epg_info['name']
                tn = epg_dn_split[1].replace('tn-', '')
                if tn in epgs_per_tenant:
                    epgs_per_tenant[tn] += 1
                else:
                    epgs_per_tenant[tn] = 1
            
            for tn, epg_count in epgs_per_tenant.items():
                docs.append({'evoaci.fabric_name': self.fabric_name,
                             'evoaci.doc_type': 'aci_epgs_per_tenant',
                             'evoaci.tenant.name': tn,
                             'evoaci.tenant.epg_count': epg_count})

            return {'rc': 0, 'data': docs}
        
        except Exception as error:
            return {'rc': 1, 'error_msgs': [f'{f_name} - {str(error)}']}

    def aci_get_leaf_stats(self):
        f_name = sys._getframe().f_code.co_name
        result = self.refresh_connection()
        if result['rc'] == 1:
            return {'rc': 1, 'error_msgs': result['error_msgs']}
        try:
            docs = []
            # Leaf Forward Scale Profile (Optional)
            uri = "https://{0}/api/node/class/topoctrlFwdScaleProf.json".format(self.apic_address)
            response = self.session.get(uri, headers=self.headers, cookies=self.cookie, verify=False).json()
            node_fwdprof = {}
            if response['imdata']:
                for item in response['imdata']:
                    node_fwdprof_item = item['topoctrlFwdScaleProf']['attributes']
                    node_dn = '/'.join(node_fwdprof_item['dn'].split('/')[0:3])
                    if node_dn in self.fabric_inventory:
                        current_fwdprof = node_fwdprof_item.get('currentProfile', '')
                        prof_type = node_fwdprof_item['profType']
                        if current_fwdprof:
                            current_fwdprof_name = current_fwdprof.split('/')[5].replace('cfgent-', '')
                        else:
                            current_fwdprof_name = 'default'
                        node_fwdprof[node_dn] = {'current_fwdprof_name': current_fwdprof_name,
                                                        'prof_type': prof_type}
            #pprint(node_fwdprof)

            uri = "https://{0}/api/node/class/configprofileEntity.json".format(self.apic_address)
            response = self.session.get(uri, headers=self.headers, cookies=self.cookie, verify=False).json()
            node_fwdprof_limits = {}
            if response['imdata']:
                for item in response['imdata']:
                    node_limits = item['configprofileEntity']['attributes']
                    node_dn = '/'.join(node_limits['dn'].split('/')[0:3])
                    if node_dn in node_fwdprof:
                        current_fwdprof_name = node_fwdprof[node_dn]['current_fwdprof_name']
                        if current_fwdprof_name == node_limits['name']:
                            if node_dn not in node_fwdprof_limits:
                                node_fwdprof_limits[node_dn] = {'bd': node_limits['bd'],
                                                                'epIpv4': node_limits['epIpv4'],
                                                                'epMac': node_limits['epMac'],
                                                                'epg': node_limits['epg'],
                                                                'lpm': node_limits['lpm'],
                                                                'policy': node_limits['policy'],
                                                                'slash32': node_limits['slash32'],
                                                                'vlan': node_limits['vlan'],
                                                                'vrf': node_limits['vrf']}
            #pprint(node_fwdprof_limits)

            uri = "https://{0}//api/node/class/ctxClassCnt.json".format(self.apic_address)
            options = "?rsp-subtree-class=l2BD,fvEpP,l3Dom"
            uri += options

            response = self.session.get(uri, headers=self.headers, cookies=self.cookie, verify=False).json()
            node_ctx_status = {}
            if response['imdata']:
                for item in response['imdata']:
                    item_data = item['ctxClassCnt']['attributes']
                    node_dn = '/'.join(item_data['dn'].split('/')[0:3])
                    if node_dn in self.fabric_inventory:
                        node_ctx_status.setdefault(node_dn, {}).update({item_data['name']: int(item_data['count'])})

            #pprint(node_ctx_status)

            uri = "https://{0}/api/class/eqptcapacityEntity.json".format(self.apic_address)
            options = '?query-target=self&rsp-subtree-include=stats&rsp-subtree-class=eqptcapacityPrefixEntries5min,eqptcapacityPolOTCAMEntry5min,eqptcapacityPolUsage5min'
            uri += options
            response = self.session.get(uri, headers=self.headers, cookies=self.cookie, verify=False).json()
            node_eqpt_capacity = {}
            if response['imdata']:
                for item in response['imdata']:
                    item_data = item['eqptcapacityEntity']['attributes']
                    node_dn = '/'.join(item_data['dn'].split('/')[0:3])
                    if node_dn in self.fabric_inventory:
                        for child in item['eqptcapacityEntity']['children']:
                            if 'eqptcapacityPolOTCAMEntry5min' in child:
                                child_data = child['eqptcapacityPolOTCAMEntry5min']['attributes']
                                key = 'PolOTCAM'
                                value = int(child_data['normalizedLast'])
                            elif 'eqptcapacityPolUsage5min' in child:
                                child_data = child['eqptcapacityPolUsage5min']['attributes']
                                key = 'PolCAM'
                                value = int(child_data['polUsageCum']) - int(child_data['polUsageBase'])
                            elif 'eqptcapacityPrefixEntries5min' in child:
                                child_data = child['eqptcapacityPrefixEntries5min']['attributes']
                                key = 'LPM'
                                value = int(child_data['extNormalizedLast'])
                            node_eqpt_capacity.setdefault(node_dn, {}).update({key: value})
            
            node_capacity_result = []

            for k,v in node_eqpt_capacity.items():
                if k in node_fwdprof_limits and k in node_ctx_status: 
                    node_capacity_result.append({'evoaci.dn': k,
                                                    'evoaci.fabric_name': self.fabric_name,
                                                    'evoaci.hlq': self.fabric_name + '/' + k,
                                                    'evoaci.doc_type': 'aci_node_limits',
                                                    'evoaci.leaf_lpm_usage': v['LPM'],
                                                    'evoaci.leaf_policy_usage': v['PolCAM'],
                                                    'evoaci.leaf_polOTcam_usage': v['PolOTCAM'],
                                                    'evoaci.leaf_bd_limit': int(node_fwdprof_limits[k]['bd']),
                                                    'evoaci.leaf_epIpv4_limit': int(node_fwdprof_limits[k]['epIpv4']),
                                                    'evoaci.leaf_epMac_limit': int(node_fwdprof_limits[k]['epMac']),
                                                    'evoaci.leaf_epg_limit': int(node_fwdprof_limits[k]['epg']),
                                                    'evoaci.leaf_lpm_limit': int(node_fwdprof_limits[k]['lpm']),
                                                    'evoaci.leaf_policy_limit': int(node_fwdprof_limits[k]['policy']),
                                                    'evoaci.leaf_slash32_limit': int(node_fwdprof_limits[k]['slash32']),
                                                    'evoaci.leaf_vlan_limit': int(node_fwdprof_limits[k]['vlan']),
                                                    'evoaci.leaf_vrf_limit': int(node_fwdprof_limits[k]['vrf']),
                                                    'evoaci.leaf_bd_usage': int(node_ctx_status[k]['l2BD']),
                                                    'evoaci.leaf_epg_usage': int(node_ctx_status[k]['fvEpP']),
                                                    'evoaci.leaf_vrf_usage': int(node_ctx_status[k]['l3Dom'])})

            return {'rc': 0, 'data': node_capacity_result}

        except Exception as error:
            return {'rc': 1, 'error_msgs': [f'{f_name} - {str(error)}']}

    def aci_get_rules(self):
        f_name = sys._getframe().f_code.co_name
        result = self.refresh_connection()
        if result['rc'] == 1:
            return {'rc': 1, 'error': result['error']}
        try:
            docs = []
            rules_count = {}
            for inv_node_dn in self.fabric_inventory:
                uri = "https://{0}/api/node/class/{1}/actrlRule.json".format(self.apic_address, inv_node_dn)
                options = '?query-target-filter=eq(actrlRule.type, "tenant")'
                uri += options
                response = self.session.get(uri, headers=self.headers, cookies=self.cookie, verify=False).json()
                if response['imdata']:
                    for item in response['imdata']:
                        if item.get('actrlRule'):
                            rule = item['actrlRule']['attributes']
                            if rule['type'] == 'tenant' and rule.get('ctrctName', ''):
                                ctrctName = rule['ctrctName']
                                node_dn = '/'.join(rule['dn'].split('/')[0:3])
                                hlq = self.fabric_name + '/' + node_dn
                                if hlq in rules_count:
                                    if ctrctName in rules_count[hlq]:
                                        rules_count[hlq][ctrctName] += 1
                                    else:
                                        rules_count[hlq].update({ ctrctName: 1 })
                                else:
                                    rules_count[hlq] = { ctrctName: 1}

            if rules_count:
                for hlq, contracts in rules_count.items():
                    for contract,count in contracts.items():
                        docs.append({'evoaci.fabric_name': self.fabric_name,
                                     'evoaci.hlq': hlq,
                                     'evoaci.doc_type': 'aci_leaf_contract_rules',
                                     'evoaci.leaf_contract': contract,
                                     'evoaci.leaf_contract_rule_count': count
                                    })
            return {'rc': 0, 'data': docs}

        except Exception as error:
            return {'rc': 1, 'error_msgs': [f'{f_name} - {str(error)}']}

    def aci_get_leaf_mem_util(self):
        f_name = sys._getframe().f_code.co_name
        result = self.refresh_connection()
        if result['rc'] == 1:
            return {'rc': 1, 'error_msgs': result['error_msgs']}
        try:
            elastic_docs = []
            for node_dn in self.fabric_inventory:
                uri = "https://{0}/api/node/mo/{1}/sys/procsys/HDprocSysMem5min-0.json".format(self.apic_address, node_dn)
                response = self.session.get(uri, headers=self.headers, cookies=self.cookie, verify=False).json()
                if response['imdata']:
                    if len(response['imdata']) == 1:
                        if response['imdata'][0].get('procSysMemHist5min', []):
                            item_data = response['imdata'][0]['procSysMemHist5min']['attributes']
                            mem_used = int(item_data['usedMax'])
                            mem_total = int(item_data['totalMax'])
                            mem_used_percent = round((mem_used/mem_total)*100, 2)
                            elastic_docs.append({'evoaci.fabric_name': self.fabric_name,
                                                'evoaci.hlq': self.fabric_name + '/' + node_dn,
                                                'evoaci.doc_type': 'aci_leaf_mem_util',
                                                'evoaci.leaf_mem_used': mem_used,
                                                'evoaci.leaf_mem_total': mem_total,
                                                'evoaci.leaf_mem_used_percent': mem_used_percent})

            return {'rc': 0, 'data': elastic_docs}

        except Exception as error:
            return {'rc': 1, 'error_msgs': [f'{f_name} - {str(error)}']}

    def aci_get_leaf_ssd_status(self):
        f_name = sys._getframe().f_code.co_name
        result = self.refresh_connection()
        if result['rc'] == 1:
            return {'rc': 1, 'error_msgs': result['error_msgs']}
        try:
            uri = "https://{0}/api/node/class/eqptFlash.json".format(self.apic_address)
            response = self.session.get(uri, headers=self.headers, cookies=self.cookie, verify=False).json()
            elastic_docs = []
            if response['imdata']:
                for item in response['imdata']:
                    item_data = item['eqptFlash']['attributes']
                    node_dn = '/'.join(item_data['dn'].split('/')[0:3])
                    if node_dn in self.fabric_inventory:
                        warning = item_data['warning']
                        elastic_docs.append({'evoaci.fabric_name': self.fabric_name,
                                             'evoaci.hlq': self.fabric_name + '/' + node_dn,
                                             'evoaci.doc_type': 'aci_leaf_ssd_warning',
                                             'evoaci.ssd_warning': warning})

            return {'rc': 0, 'data': elastic_docs}

        except Exception as error:
            return {'rc': 1, 'error_msgs': [f'{f_name} - {str(error)}']}

    def aci_get_fabric_inventory(self):
        f_name = sys._getframe().f_code.co_name
        result = self.refresh_connection()
        if result['rc'] == 1:
            return {'rc': 1, 'error_msgs': result['error_msgs']}
        try:
            docs = []
            result = self.aci_get_class('fabricNode')
            if result['rc'] == 0:
                inv_list = result['data']
                for item in inv_list:
                    item_dict = item['fabricNode']['attributes']
                    # Including Leaf switches only, if Spines needed, add OR spine statement
                    if item_dict['role'] == 'leaf':
                        inv_dict = {}
                        inv_dict['device'] = item_dict['name']
                        inv_dict['serial'] = item_dict['serial']
                        inv_dict['model'] = item_dict['model']
                        inv_dict['dn'] = item_dict['dn']
                        inv_dict['ip'] = item_dict['address']
                        inv_dict['sw_version'] = item_dict['version']
                        self.fabric_inventory[item_dict['dn']] = inv_dict
                        docs.append({'host.name': inv_dict['device'],
                                     'evoaci.doc_type': 'aci_leaf_inventory',
                                     'evoaci.hlq': self.fabric_name + '/' + inv_dict['dn'],
                                     'evoaci.dn': inv_dict['dn'],
                                     'evoaci.fabric_name': self.fabric_name,
                                     'host.os.version': inv_dict['sw_version'],
                                     'host.type': inv_dict['model'],
                                     'host.ip': inv_dict['ip'],
                                     'host.serial': inv_dict['serial']})

                if self.fabric_inventory and docs:
                    return {'rc': 0 , 'data': docs }
            else:
                return {'rc': 1, 'error_msgs': result['error_msgs'] }

        except Exception as error:
            return {'rc': 1, 'error_msgs': [f'{f_name} - {str(error)}']}

    def aci_get_rpmEntity(self):
        f_name = sys._getframe().f_code.co_name
        docs = []
        errors = []
        result = self.refresh_connection()
        if result['rc'] == 1:
            return {'rc': 1, 'error_msgs': result['error_msgs']}
        try:
            result = self.aci_get_class('rpmEntity')
            if result['rc'] != 0:
                errors.extend(result['error_msgs'])
                return {'rc': 1, 'error_msgs': errors}

            result_data = result['data']
            for item in result_data:
                if item.get('rpmEntity'):
                    dn = item['rpmEntity']['attributes']['dn']
                    node_dn = '/'.join(dn.split('/')[0:3])
                    pod = dn.split('/')[1].replace('pod-', '')
                    node = dn.split('/')[2].replace('node-', '')
                    if node_dn in self.fabric_inventory:
                        docs.append({'host.name': self.fabric_inventory[node_dn]['device'],
                                     'evoaci.doc_type': 'aci_leaf_rpm',
                                     'evoaci.mo': 'rpmEntity',
                                     'evoaci.hlq': self.fabric_name + '/' + node_dn,
                                     'evoaci.pod': pod,
                                     'evoaci.node': node,
                                     'evoaci.fabric_name': self.fabric_name,
                                     'evoaci.shMemAllocFailCount': int(item['rpmEntity']['attributes'].get('shMemAllocFailCount', 0)),
                                     'evoaci.shMemTotal': int(item['rpmEntity']['attributes'].get('shMemTotal', 0)),
                                     'evoaci.shMemUsage': int(item['rpmEntity']['attributes'].get('shMemUsage', 0)),
                                     'evoaci.shMemAlert': item['rpmEntity']['attributes'].get('shMemAlert', '')
                                    })

            return {'rc': 0 , 'data': docs }

        except Exception as error:
            return {'rc': 1, 'error_msgs': [f'{f_name} - {str(error)}']}

    def aci_get_extepg_count(self):
        f_name = sys._getframe().f_code.co_name
        docs = []
        errors = []
        result = self.refresh_connection()
        if result['rc'] == 1:
            return {'rc': 1, 'error_msgs': result['error_msgs']}
        try:
            epg_counts = {}
            count_field = 'fvRtdEpP' + '_count'
            result = self.aci_get_class('fvRtdEpP')
            ext_epgs = result['data']
            for ext_epg in ext_epgs:
                ext_epg_dn = ext_epg['fvRtdEpP']['attributes']['dn']
                l3out_dn = '/'.join(ext_epg_dn.split('[')[1].split('/')[:-1])
                result = self.aci_get_mo(l3out_dn, 'l3extLNodeP')
                l3outs_with_children = result['data']
                for l3out_with_children in l3outs_with_children:
                    if 'children' in l3out_with_children['l3extOut']:
                        node_profs = l3out_with_children['l3extOut']['children']
                        for node_prof in node_profs:
                            node_prof_rn = node_prof['l3extLNodeP']['attributes']['rn']
                            node_prof_dn = l3out_dn + '/' + node_prof_rn
                            result = self.aci_get_mo(node_prof_dn, 'l3extRsNodeL3OutAtt')
                            node_profs_with_children = result['data']
                            for node_prof_with_children in node_profs_with_children:
                                l3outattrs = node_prof_with_children['l3extLNodeP']['children']
                                for l3outattr in l3outattrs:
                                    node_dn = l3outattr['l3extRsNodeL3OutAtt']['attributes']['tDn']
                                    if node_dn in epg_counts.keys():
                                        epg_counts[node_dn] += 1
                                    else:
                                        epg_counts[node_dn] = 1

            for node_dn, epg_count in epg_counts.items():
                if self.fabric_inventory.get(node_dn):
                    pod = node_dn.split('/')[1].replace('pod-', '')
                    node = node_dn.split('/')[2].replace('node-', '')
                    if node_dn in self.fabric_inventory:
                        docs.append({'evoaci.doc_type': 'aci_extepg_per_leaf',
                                     'host.name': self.fabric_inventory[node_dn]['device'],
                                     'evoaci.mo': 'fvRtdEpP',
                                     'evoaci.hlq': self.fabric_name + '/' + node_dn,
                                     'evoaci.pod': pod,
                                     'evoaci.node': node,
                                     'evoaci.fabric_name': self.fabric_name,
                                     'evoaci.epg_count': epg_count
                                    })

            return {'rc': 0 , 'data': docs }

        except Exception as error:
            return {'rc': 1, 'error_msgs': [f'{f_name} - {str(error)}']}

    def aci_get_l3outs(self):
        f_name = sys._getframe().f_code.co_name
        docs = []
        errors = []
        result = self.refresh_connection()
        if result['rc'] == 1:
            return {'rc': 1, 'error_msgs': result['error_msgs']}
        try:
            epg_counts = {}
            count_field = 'evoaci.'+ 'l3extInstP' + '_count'
            result = self.aci_get_class('l3extInstP')
            ext_epgs = result['data']
            for ext_epg in ext_epgs:
                ext_epg_dn = ext_epg['l3extInstP']['attributes']['dn']
                l3out_dn = '/'.join(ext_epg_dn.split('/')[:-1])
                result = self.aci_get_mo(l3out_dn, 'l3extLNodeP')
                l3outs_with_children = result['data']
                for l3out_with_children in l3outs_with_children:
                    if 'children' in l3out_with_children['l3extOut']:
                        node_profs = l3out_with_children['l3extOut']['children']
                        for node_prof in node_profs:
                            node_prof_rn = node_prof['l3extLNodeP']['attributes']['rn']
                            node_prof_dn = l3out_dn + '/' + node_prof_rn
                            result = self.aci_get_mo(node_prof_dn, 'l3extRsNodeL3OutAtt')
                            node_profs_with_children = result['data']
                            for node_prof_with_children in node_profs_with_children:
                                l3outattrs = node_prof_with_children['l3extLNodeP']['children']
                                for l3outattr in l3outattrs:
                                    node_dn = l3outattr['l3extRsNodeL3OutAtt']['attributes']['tDn']
                                    if node_dn in epg_counts.keys():
                                        epg_counts[node_dn] += 1
                                    else:
                                        epg_counts[node_dn] = 1
            for node_dn, epg_count in epg_counts.items():
                if node_dn in self.fabric_inventory:
                    pod = node_dn.split('/')[1].replace('pod-', '')
                    node = node_dn.split('/')[2].replace('node-', '')
                    docs.append({'evoaci.doc_type': 'aci_extepg_per_l3out',
                                'host.name': self.fabric_inventory[node_dn]['device'],
                                'evoaci.mo': 'l3extInstP',
                                'evoaci.hlq': self.fabric_name + '/' + node_dn,
                                'evoaci.pod': pod,
                                'evoaci.node': node,
                                'evoaci.fabric_name': self.fabric_name,
                                count_field: epg_count,
                                })
            return {'rc': 0 , 'data': docs }

        except Exception as error:
            return {'rc': 1, 'error_msgs': [f'{f_name} - {str(error)}']}

    def aci_get_ports_capacity(self):
        f_name = sys._getframe().f_code.co_name
        if self.fabric_inventory:
            result = self.refresh_connection()
            if result['rc'] == 1:
                return {'rc': 1, 'error_msgs': result['error_msgs']}
            try:
                docs = []
                for dn, device in self.fabric_inventory.items():

                    ports_up = ports_down = ports_disabled = ports_total = 0

                    dn = device['dn']
                    pod = dn.split('/')[1].replace('pod-', '').strip()
                    node = dn.split('/')[2].replace('node-', '').strip()
                    uri = "https://{0}/api/node/class/topology/pod-{1}/node-{2}/l1PhysIf.json?rsp-subtree=children" \
                          "&rsp-subtree-class=ethpmPhysIf".format(self.apic_address, pod, node)

                    response = self.session.get(uri, headers=self.headers, cookies=self.cookie, verify=False)
                    if response.status_code == 200:

                        response_data = response.json()

                        if response_data['imdata']:

                            for item in response_data['imdata']:
                                ports_total += 1
                                port_info = item['l1PhysIf']['attributes']
                                adminSt = port_info['adminSt']
                                operSt = ''
                                if 'children' in item['l1PhysIf']:
                                    if 'ethpmPhysIf' in item['l1PhysIf']['children'][0]:
                                        operSt = item['l1PhysIf']['children'][0]['ethpmPhysIf']['attributes']['operSt']
                            
                                if operSt == 'down':
                                    if adminSt == 'down':
                                        ports_disabled += 1
                                    else:
                                        ports_down += 1
                                elif operSt == 'up':
                                    ports_up += 1

                            ports_free = ports_total - ports_up
                            ports_util_percent = 100*ports_up/ports_total

                            docs.append({'host.name': device['device'],
                                         'evoaci.dn': dn,
                                         'evoaci.doc_type': 'aci_port_capacity',
                                         'evoaci.hlq': self.fabric_name + '/' + dn,
                                         'evoaci.fabric_name': self.fabric_name,
                                         'evoaci.ports_total': ports_total,
                                         'evoaci.ports_free': ports_free,
                                         'evoaci.ports_disabled': ports_disabled,
                                         'evoaci.ports_down': ports_down,
                                         'evoaci.ports_util_percent': round(ports_util_percent, ndigits=1),
                                         'evoaci.ports_up': ports_up})
                if docs:
                    return {'rc': 0, 'data': docs }

            except Exception as error:
                return {'rc': 1, 'error_msgs': [f'{f_name} - {str(error)}']}


    def count_by_pod_node(self, mo):
        f_name = sys._getframe().f_code.co_name
        docs = []
        data_counts = {}
        errors = []
        count_field = 'evoaci.' + mo + '_count'
        result = self.refresh_connection()
        if result['rc'] == 1:
            return {'rc': 1, 'error_msgs': result['error_msgs']}
        try:
            result = self.aci_get_class(mo)
            result_data = result['data']
            # Set hlq-dn for each doc. hlq format is topology/pod/node
            for item in result_data:
                if item.get(mo):
                    node_dn = '/'.join(item[mo]['attributes']['dn'].split('/')[0:3])
                    if node_dn in data_counts.keys():
                        data_counts[node_dn] += 1
                    else:
                        data_counts[node_dn] = 1
            for node_dn, data_count in data_counts.items():
                pod = node_dn.split('/')[1].replace('pod-', '')
                node = node_dn.split('/')[2].replace('node-', '')
                if node_dn in self.fabric_inventory:
                    docs.append({'host.name': self.fabric_inventory[node_dn]['device'],
                                'evoaci.doc_type': 'aci_mo_count_by_pod_node',
                                'evoaci.mo': mo,
                                'evoaci.hlq': self.fabric_name + '/' + node_dn,
                                'evoaci.pod': pod,
                                'evoaci.node': node,
                                'evoaci.fabric_name': self.fabric_name,
                                count_field: data_count,
                                })
        
            
            return {'rc': 0 , 'data': docs }

        except Exception as error:
            return {'rc': 1, 'error_msgs': [f'{f_name} - {error}']}


# ACI Scalability collector function
def aci_scale(config_data):
    error_msgs = []
    elastic_docs = []
    # Reformat parameters
    apics = {config_data["hostname"]:
            [
                {
                    'address': config_data["hostip"],
                    'username': config_data["username"],
                    'password': config_data["password"]
                    }
                ]
            }
    config_data["apics"] = apics
    # Instantiate APIC
    apic = Apic(fabrics=config_data['apics'])
    for fabric_name in config_data['apics'].keys():
        login_result = apic.login(fabric_name)
        if login_result['rc'] != 0:
            error_msgs.extend(login_result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}

        # Get inventory
        result = apic.aci_get_fabric_inventory()
        if result['rc'] != 0:
            error_msgs.extend(result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}
        else:
            elastic_docs.extend(result['data'])

        result = apic.aci_get_fabric_usage()
        if result['rc'] != 0:
            error_msgs.extend(result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}
        else:
            elastic_docs.extend(result['data'])

        result = apic.aci_get_leaf_mem_util()
        if result['rc'] != 0:
            error_msgs.extend(result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}
        else:
            elastic_docs.extend(result['data'])

        result = apic.aci_get_leaf_ssd_status()
        if result['rc'] != 0:
            error_msgs.extend(result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}
        else:
            elastic_docs.extend(result['data'])

        result = apic.aci_get_leaf_stats()
        if result['rc'] != 0:
            error_msgs.extend(result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}
        else:
            elastic_docs.extend(result['data'])
            
        # Get port capacity
        result = apic.aci_get_ports_capacity()
        if result['rc'] != 0:
            error_msgs.extend(result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}
        else:
            elastic_docs.extend(result['data'])

        ## Get rpmEntity objects
        result = apic.aci_get_rpmEntity()
        if result['rc'] != 0:
            error_msgs.extend(result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}
        else:
            elastic_docs.extend(result['data'])

        ## Get rtmapRule objects
        result = apic.count_by_pod_node('rtmapRule')
        if result['rc'] != 0:
            error_msgs.extend(result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}
        else:
            elastic_docs.extend(result['data'])

        ## Get rtmapEntry objects
        result = apic.count_by_pod_node('rtmapEntry')
        if result['rc'] != 0:
            error_msgs.extend(result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}
        else:
            elastic_docs.extend(result['data'])

        ## Get rtpfxEntry objects
        result = apic.count_by_pod_node('rtpfxEntry')
        if result['rc'] != 0:
            error_msgs.extend(result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}
        else:
            elastic_docs.extend(result['data'])

        ## # Get fvRtdEpP objects
        result = apic.aci_get_rpmEntity()
        if result['rc'] != 0:
            error_msgs.extend(result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}
        else:
            elastic_docs.extend(result['data'])

        # Get actrlPfxEntry objects
        result = apic.count_by_pod_node('actrlPfxEntry')
        if result['rc'] != 0:
            error_msgs.extend(result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}
        else:
            elastic_docs.extend(result['data'])

        # Get actrlRule objects
        result = apic.count_by_pod_node('actrlRule')
        if result['rc'] != 0:
            error_msgs.extend(result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}
        else:
            elastic_docs.extend(result['data'])

        # Get l3extInstP objects
        result = apic.aci_get_l3outs()
        if result['rc'] != 0:
            error_msgs.extend(result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}
        else:
            elastic_docs.extend(result['data'])
        
        # Get Leaf Contract Rules Count
        result = apic.aci_get_rules()
        if result['rc'] != 0:
            error_msgs.extend(result['error_msgs'])
            return {'rc': 1, 'elastic_docs': elastic_docs, 'error_msgs': error_msgs}
        else:
            elastic_docs.extend(result['data'])

        apic.disconnect()

        return {'rc': 0, 'elastic_docs': elastic_docs, 'error_msgs': []}

#>>>>
# Custom Python code ended here

# Define Ansible module args
module_args = {
    "hostname": {"required": True, "type": "str"},
    "hostip": {"required": True, "type": "str"},
    "username": {"required": True, "type": "str"},
    "password": {"required": True, "type": "str", "no_log": True},
}

# Initialise the result dictionary
result = {
    "changed": False,
    "elastic_docs": [],
    "errors": [],
    "messages": [],
    "debug": []
} 

# Instantiate AnsibleModule
module = AnsibleModule(argument_spec=module_args)
config_data = {}
# Mandatory parameters stored in Dictionary and passed to custom python code
config_data["hostname"] = module.params["hostname"]
config_data["hostip"] = module.params["hostip"]
config_data["username"] = module.params["username"]
config_data["password"] = module.params["password"]

collector_result = aci_scale(config_data)

# If successful result from the Python collector, return module.exit_json() as below, or otherwise module.fail_json()

if collector_result["rc"]:
    result["errors"] = collector_result["error_msgs"]
    result["elastic_docs"] = []
    module.fail_json(msg=f'ACI Collector failed.', **result)
else:
    result["elastic_docs"] = collector_result["elastic_docs"]
    module.exit_json(**result)
