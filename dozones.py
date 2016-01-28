#!/usr/bin/python
# dozones.py - Scott Harney <sharney@virtual.com>
#
# from generated zoning list, create zones on Cisco MDS switches
# requires netmiko from https://github.com/ktbyers/netmiko/tree/master/netmiko


import sys    
import argparse
import os
import getpass
import time
sys.path.append("./library")
from na_funcs import *
from cisco_funcs import *
debug = False

# parse command line arguments and optional environment variables
arguments = argparse.ArgumentParser(
    description='push zoning configuration to MDS switch from generated command file. Zoneset name and VSAN are derived form the input file.')
arguments.add_argument(
    '--hostname', required=True, type=str,
    help='MDS switch fqdn or IP.')
arguments.add_argument(
    '--filename', required=True, type=str,
    help='Generated file with zoning commands to push to the mds switch.')
arguments.add_argument(
    '--username', required=False, type=str,
    help='optional username to ssh into mds switch. Alternate: set environment variable MDS_USERNAME. If neither exists, defaults to current OS username') 
arguments.add_argument(
    '--password', required=False, type=str,
    help='optional password to ssh into mds switch. Alternate: set environment variable MDS_PASSWORD. If unset use_keys defaults to True.') 
arguments.add_argument(
    '--use_keys',  action='store_true',
    help='use ssh keys to log into switch') 
arguments.add_argument(
    '--dry_run', default=False, action='store_true',
    help='don\'t do anything. just print some debug output') 
arguments.add_argument(
    '--key_file',  required=False, type=str,
    help='filename for ssh key file') 
arguments.add_argument(
    '--activate_zoneset',  action='store_true',
    help='add the \'zoneset activate\' command to activate the updated zoneset') 
args = arguments.parse_args()

if args.password :
    use_keys = False
    password = args.password
elif os.getenv('MDS_PASSWORD') :
    use_keys = False
    password = os.getenv('MDS_PASSWORD')
else :
    use_keys = True
    password = ''

if args.username :
    username = args.username
elif os.getenv('MDS_USERNAME') :
    username = os.getenv('MDS_USERNAME')
else:
    username = getpass.getuser()

if args.activate_zoneset :
    activate = True
else :
    activate = False
    
mds = args.hostname
zone_commands_filename = args.filename
keyfile = args.key_file
dry_run = args.dry_run

if not has_netmiko :
    print "netmiko is required to use this script, download installation from:"
    print "https://github.com/ktbyers/netmiko/tree/master/netmiko"
    exit(1)

# call nonblank_lines to clean up input and load command set into list variable.
commands = []
with open(zone_commands_filename) as f_in:
    for line in nonblank_lines(f_in) :
        if "zoneset name ZS_" in line : # populating zoneset & vsan based on simple pattern matching. this is a hack.
            zoneset_line = line.split()
            zoneset = zoneset_line[2]
            vsan = zoneset_line[4]
        else:
            commands.append(line)

# commend to mds
mds = {
    'device_type': 'cisco_nxos',
    'ip': mds,
    'verbose': False,
    'username': username,
    'password': password,
    'use_keys': use_keys
}

# def handle_mds_continue(net_connect, cmd):
#     net_connect.remote_conn.sendall(cmd)
#     time.sleep(1)
#     output = net_connect.remote_conn.recv(65535).decode('utf-8')       
#     if 'want to continue' in output:
#         net_connect.remote_conn.sendall('y\n')
#         output += net_connect.remote_conn.recv(65535).decode('utf-8')
#         return output   

net_connect = ConnectHandler(**mds)

if dry_run :
    output = net_connect.find_prompt()
    print "DRY RUN: prompt = %s" % output

#uncomment lines below to actually do this
if not dry_run :
    output = net_connect.send_config_set(commands)
    print output
else :
    print "DRY RUN: command list = %r" % commands
    
zoneset_command = "zoneset activate name %s vsan %s\n" % (zoneset,vsan)
if activate and not dry_run :
    net_connect.config_mode()
    output = handle_mds_continue(net_connect, cmd=zoneset_command)
    print output
    net_connect.exit_config_mode()
    net_connect.send_command('copy run start')
elif dry_run and not activate :
    print "DRY RUN: no activate command"
else :
    print "DRY RUN: activate command = %r" % zoneset_command

net_connect.disconnect()
