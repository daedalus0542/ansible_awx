#!/usr/bin/env python
import requests
import json
import os
import sys
import argparse

class AKIPSAnsibleAWXDevices(object):
    def __init__(self):
        self.inventory = {}
        self.read_cli_args()

        # Called with `--list`.
        self.inventory = self.getAKIPSDeviceList()
        print(json.dumps(self.inventory))

    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action = 'store_true')
        parser.add_argument('--host', action = 'store')
        self.args = parser.parse_args()
        
    def getAKIPSDeviceList(self):
        #Custom credential type that has the akips api password
        passwd = os.environ.get("bpasswd")
        dev_grp = os.environ.get("akips_dev_grp")

        #replace <proxy_ip> with proxy ip address
        proxy = {'http': 'http://<proxy_ip>:80'}
        ansible_awx_device_list = {
            dev_grp: {
                    'hosts': [],
                    'vars': {
                        'host_key_checking': "False"
                    }
                },
                '_meta': {
                    'hostvars': {}
                },
            "cisco": {
                    'hosts': [],
                    'vars': {
                        'host_key_checking': "False"
                    }
                },
                '_meta': {
                    'hostvars': {}
                }
            }
    
        dev_hostvars = {
        }
    
        #Retrieve list of devices from akips
        #replace <akips_ip_address> with akips ip address
        url = ("https://<akips_ip_address>/api-db?password=" + passwd + ";cmds=mget text * sys ip4addr any group " + dev_grp)
        response_device_dtl = requests.get(url, verify=False)
    
        device_dtl = response_device_dtl.text.replace('sys ip4addr = ', 'ansible_host:')
    
        device_dtl_list = device_dtl.split("\n")
        device_dtl_list.pop()
    
        for device_line in device_dtl_list:
            device_list = device_line.split(" ")
    
            hostname = device_list[0]
            dev_vars = device_list[1].split(":")
    
            ansible_awx_device_list[dev_grp]["hosts"].append(hostname)
            ansible_awx_device_list["cisco"]["hosts"].append(hostname)
            host_details = "{\"%s\":\"%s\"}" % (dev_vars[0], dev_vars[1])
            host_details = json.loads(host_details)

            ansible_awx_device_list["_meta"]["hostvars"][hostname] = host_details
    
        return(ansible_awx_device_list)

AKIPSAnsibleAWXDevices()
