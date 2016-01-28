#!/usr/bin/python
# checkwwpngroupfcaliases.py
#
# interrogate a NetApp cDOT cluster to retrive an igroup list of WWPNs and compare that against
# a cisco mds switch list of fcaliases.


import sys
import argparse
import os
import getpass
import time
import pprint
sys.path.append("./library")
from na_funcs import *
from cisco_funcs import *
debug = False

# parse command line arguments and optional environment variables

arguments = argparse.ArgumentParser(
    description='Provide an igroup and filer and check the wwpns in that igroup are defined as fcaliases on an mds switch')
arguments.add_argument(
    '--switch_hostname', required=True, type=str,
    help='MDS switch fqdn or IP.')
arguments.add_argument(
    '--filer_hostname', required=True, type=str,
    help='filer fqdn or IP.')
arguments.add_argument(
    '--igroup', required=True, type=str,
     help='name of igroup on NetApp cDOT system to check')
arguments.add_argument(
    '--switch_username', required=False, type=str,
    help='optional username to ssh into mds switch. Alternate: set environment variable MDS_USERNAME. If neither exists, defaults to current OS username') 
arguments.add_argument(
    '--switch_password', required=False, type=str,
    help='optional password to ssh into mds switch. Alternate: set environment variable MDS_PASSWORD. If unset use_keys defaults to True.') 
arguments.add_argument(
    '--switch_use_keys',  action='store_true',
    help='use ssh keys to log into switch') 
arguments.add_argument(
    '--switch_key_file',  required=False, type=str,
    help='filename for ssh key file') 
arguments.add_argument(
    '--filer_username', required=False, type=str,
    help='optional username to ssh into mds switch. Alternate: set environment variable FILER_USERNAME. If neither exists, defaults to admin') 
arguments.add_argument(
    '--filer_password', required=False, type=str,
    help='optional password to ssh into mds switch. Alternate: set environment variable filer_PASSWORD. If unset use_keys defaults to True.') 

args = arguments.parse_args()

if args.switch_password :
    use_keys = False
    switch_password = args.switch_password
elif os.getenv('MDS_PASSWORD') :
    use_keys = False
    switch_password = os.getenv('MDS_PASSWORD')
else :
    switch_use_keys = True
    switch_password = ''

if args.switch_username :
    switch_username = args.switch_username
elif os.getenv('MDS_USERNAME') :
    switch_username = os.getenv('MDS_USERNAME')
else:
    switch_username = getpass.getuser()

if args.filer_password :
    filer_password = args.filer_password
elif os.getenv('FILER_PASSWORD') :
    filer_password = os.getenv('FILER_PASSWORD')
else :
    filer_password = ''

if args.filer_username :
    filer_username = args.filer_username
elif os.getenv('FILER_USERNAME') :
    filer_username = os.getenv('FILER_USERNAME')
else:
    filer_username = 'admin'


switch_hostname = args.switch_hostname
filer_hostname = args.filer_hostname
igroup = args.igroup

# main loop

mds = {
    'device_type': 'cisco_nxos',
    'ip': switch_hostname,
    'verbose': False,
    'username': switch_username,
    'password': switch_password,
    'use_keys': switch_use_keys
}

#igroup = 'JDC-Prod-01'
#filerusername = 'admin'
#filerpassword = 'netapp123'
#filerhostname = 'jdc-nac1.prod.entergy.com'

filerconnect = cdotconnect(filer_hostname,filer_username,filer_password)
wwpns = getigroupwwpns(igroup, filerconnect)

net_connect = ConnectHandler(**mds)
show_run_str = net_connect.send_command("show run")
show_run = show_run_str.splitlines()
cisco_cfg = CiscoConfParse(show_run)
fcalias_dict = parsefcaliases(cisco_cfg)
net_connect.disconnect()


if debug :
    print "DEBUG START: dump grabbed igroup WWPNs and switch fcaliases"
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(wwpns)
    pp.pprint(fcalias_dict)
    print "DEBUG END: "

for check_wwpn in wwpns :
    for key in fcalias_dict.keys() :
        if check_wwpn in fcalias_dict[key]['pwwns'] :
            print "%s in igroup %s matches fcalias name %s on mds %s vsan %s" % (check_wwpn, igroup, fcalias_dict[key]['name'], switch_hostname, fcalias_dict[key]['vsan'])
            

