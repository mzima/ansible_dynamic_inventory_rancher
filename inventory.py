#!/usr/bin/env python3
#
# Ansible dynamic inventory for Rancher
#

import os
import sys
import argparse
import json
import configparser
import requests

# Path to rancher config file
cfg_file = 'inventory.ini'

# Connection timeout
connection_timeout = 60

# Expose connection data
show_connection_data = True

try:
    import json
except ImportError:
    import simplejson as json

class Inventory(object):

    def __init__(self):
        self.inventory = {}
        self.read_cli_args()

        # Called with `--list`.
        if self.args.list:
            self.inventory = self.rancher_inventory()
        # Called with `--host [hostname]`
        elif self.args.host:
            # Not implemented, since we return _meta info `--list`.
            self.inventory = self.empty_inventory()
        # If no groups or vars are present, return an empty inventory.
        else:
            self.inventory = self.empty_inventory()

        print(json.dumps(self.inventory))
    
    # Get Rancher url and credentials from settings file
    def __settings(self, cfg_file):
        content = configparser.ConfigParser()
        content.read(cfg_file)
        return(content)

    # Rancher API query
    def __api_get(self, url, token, verify = True):
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(token)}
        response_cluster = requests.get(url, headers=headers, verify=bool(verify), timeout=connection_timeout)
        if response_cluster.status_code == 200:
            result = json.loads(response_cluster.content.decode('utf-8'))
            return(result['data'])
        else:
            print('Error accessing {0}. HTTP status code {1}.'.format(url, response_cluster.status_code))
            exit(255)

    # Build Rancher inventory
    def rancher_inventory(self):

        config = self.__settings(cfg_file)
        api_url = config['main']['rancher_url']
        api_url_base = '{0}/v3'.format(api_url)
        api_token = config['main']['rancher_token']
        ssl_verify = config['main']['ssl_verify']
        
        cluster_url = '{0}/clusters'.format(api_url_base)
        cluster_data = self.__api_get(cluster_url, api_token, ssl_verify)
        
        result = {}
        result['_meta'] = {}
        result['_meta']['hostvars'] = {}

        if show_connection_data:
            result['all'] = {}
            result['all']['vars'] = {}
            result['all']['vars']['api_url_base'] = api_url_base
        
        # Process group and host data
        for this_cluster in cluster_data:
            cluster_id = this_cluster['id']
            cluster_name = this_cluster['name']
            result[cluster_name] = {}
            result[cluster_name]['hosts'] = []
            result[cluster_name]['vars'] = {}

            host_url = '{0}/clusters/{1}/nodes'.format(api_url_base, cluster_id)
            host_data = self.__api_get(host_url, api_token, ssl_verify)

            # Host variables
            for this_host in host_data:
                try:
                    host_name = this_host['hostname']
                except KeyError:
                    continue

                result[cluster_name]['hosts'].append(host_name)
                result['_meta']['hostvars'][host_name] = {}
                result['_meta']['hostvars'][host_name]['roles'] = []
                result['_meta']['hostvars'][host_name]['host_state'] = this_host['state']
                result['_meta']['hostvars'][host_name]['host_id'] = this_host['id']
                result['_meta']['hostvars'][host_name]['cluster_name'] = cluster_name
                result['_meta']['hostvars'][host_name]['cluster_id'] = cluster_id
                result['_meta']['hostvars'][host_name]['labels'] = []
                result['_meta']['hostvars'][host_name]['labels'] = this_host['labels']

                if 'node-role.kubernetes.io/controlplane' in this_host['labels']:
                    result['_meta']['hostvars'][host_name]['roles'].append("controlplane")

                if 'node-role.kubernetes.io/worker' in this_host['labels']:
                    result['_meta']['hostvars'][host_name]['roles'].append("worker")

                if 'node-role.kubernetes.io/etcd' in this_host['labels']:
                    result['_meta']['hostvars'][host_name]['roles'].append("etcd")

            # Group component health state
            try:
                for this_component in this_cluster['componentStatuses']:
                    if 'controller-manager' in this_component['name'] or 'etcd' in this_component['name']:
                        component_id = '{0}_healthy'.format(this_component['name']).replace('-','_')
                        result[cluster_name]['vars'][component_id] = bool(this_component['conditions'][0]['status'])
            except KeyError:
                pass

            # Group variables
            group_vars = [
                'description',
                'driver',
                'id',
                'istioEnabled',
                'nodeCount',
                'state',
                ]

            for this_var in group_vars:
                result[cluster_name]['vars'][this_var] = this_cluster[this_var]

        return result

    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action = 'store_true')
        parser.add_argument('--host', action = 'store')
        self.args = parser.parse_args()

#
# Main
#

# Get the inventory.
Inventory()
