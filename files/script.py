import os
HERE = os.path.dirname(__file__)

from tabulate import tabulate
from genie.testbed import load

testbed = load(os.path.join(HERE, 'testbed.yaml'))

for device in testbed:
    device.connect()
    device_info = device.learn('platform')
    bgp = device.learn('bgp')

    # print useful information
    print('\n' + '-'*80)
    print('Hostname: %s' % device.name)
    print('Software Version: %s %s\n' % (device_info.os, device_info.version))
    
    nbr_info = []
    for bgp_instance in bgp.info['instance']:
        for vrf in bgp.info['instance'][bgp_instance]['vrf']:
            for nbr in bgp.info['instance'][bgp_instance]['vrf'][vrf]['neighbor']:
                state = bgp.info['instance'][bgp_instance]['vrf'][vrf]['neighbor'][nbr]['session_state']
                nbr_info.append((bgp_instance, vrf, nbr, state))
    
    print(tabulate(nbr_info, headers = ['BGP Instance', 'VRF', 'Neighbor', 'State']))

    active_nbr = len([i for i in nbr_info if i[-1] == 'established'])
    print('\nTotal # of Active Neighbors: %s' % active_nbr)
    print('-'*80 + '\n')
