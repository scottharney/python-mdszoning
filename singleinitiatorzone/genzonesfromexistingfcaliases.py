#!/usr/bin/python
# genzonesfromexistingfcaliases.py - Scott Harney <sharney@virtual.com>
#
# generate zoning commands given output of "show fcalias" from switch
# assumes zones have lowercase entries and single initiator zoning is used
# generates zoning commands to add new array.  List of hostnames should
# also be provided one per line in a file.
# populate relevant variables below

import sys
import argparse
import os
import getpass
import re
sys.path.append("./library")
from na_funcs import *
from cisco_funcs import *
debug = True

# parse command line arguments and optional environment variables

arguments = argparse.ArgumentParser(
    description='Generate zoning commands from input file listing of short hostnames one per line.  Will match against switch fcalias entries by hostname pattern. print to STDOUT. redirect with > filename.txt')
arguments.add_argument(
    '--hostname', required=True, type=str,
    help='MDS switch fqdn or IP.')
arguments.add_argument(
    '--hosts_filename', required=True, type=str,
    help='list of hosts to match against. one per line')
arguments.add_argument(
    '--vsan', required=True, type=str,
    help='VSAN for fcaliases/zones')
arguments.add_argument(
    '--zoneset', required=True, type=str,
    help='zoneset name')
arguments.add_argument(
    '--fcalias_filename', required=True, type=str,
    help='generated fcaliases output from \'ssh username@switchname show fcalias > switch_fcaliases.txt\'')
arguments.add_argument(
    '--target_fcalias', required=False, type=str,
    default='NAC1', help='optional fcalias name of cDOT cluster on switch. default =\'NAC1\'')
arguments.add_argument(
    '--username', required=False, type=str,
    help='optional username to ssh into mds switch. Alternate: set environment variable MDS_USERNAME. If neither exists, defaults to current OS username') 
arguments.add_argument(
    '--get_from_switch',  default=False, action='store_true',
    help='get fcaliases directly from switch instead of file. NOTE: not yet implemented') 
arguments.add_argument(
    '--password', required=False, type=str,
    help='optional password to ssh into mds switch. Alternate: set environment variable MDS_PASSWORD. If unset use_keys defaults to True.') 
arguments.add_argument(
    '--use_keys',  action='store_true',
    help='use ssh keys to log into switch') 
arguments.add_argument(
    '--backout', default=False,  action='store_true',
    help='generate backout commands') 
arguments.add_argument(
    '--key_file',  required=False, type=str,
    help='filename for ssh key file') 

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

if args.fcalias_filename and args.get_from_switch :
    print "You can get from the switch directly OR use an input file of fcaliases. pick one."
    exit (1)
    
switch_hostname = args.hostname
hostname_filename = args.hosts_filename
if args.fcalias_filename:
    fcalias_filename = args.fcalias_filename
    
NAfcalias = args.target_fcalias
keyfile = args.key_file
vsan = args.vsan
zoneset = args.zoneset
backout = args.backout

hostnames = open(hostname_filename, "r").readlines()

if args.get_from_switch :
    # connect to mds
    mds = {
        'device_type': 'cisco_nxos',
        'ip': switch_hostname,
        'verbose': False,
        'username': username,
        'password': password,
        'use_keys': use_keys
    }
    net_connect = ConnectHandler(**mds)
    show_fcaliases = net_connect.send_command("show fcalias")
    fcaliases = show_fcaliases.splitlines()
else:
    fcaliases = open(fcalias_filename, "r").readlines()

esxfcaliases = []
zones = []
for host in hostnames :
    hostpattern = ".*%s.*" % host.strip()
    checkhost = re.compile(hostpattern, re.IGNORECASE)
    for fcalias in fcaliases:
        if checkhost.search(fcalias):
            esxhost = fcalias.split()
            esxfcaliases.append(esxhost[2])
            zones.append("%s_%s" % (esxhost[2], NAfcalias))
        
if not backout:    
    for esxfcalias in esxfcaliases :
        print "zone name %s_%s vsan %s" % (esxfcalias, NAfcalias, vsan)
        print "   member fcalias %s" % NAfcalias
        print "   member fcalias %s" % esxfcalias
        print "\n"

    print "zoneset name %s vsan %s" % (zoneset, vsan)
    for zone in zones :
        print "   member %s" % zone
else :
    print "\n"
    print "zoneset name %s vsan %s" % (zoneset, vsan)
    for zone in zones :
        print "no member %s" % zone
    print "\n"
    for esxfcalias in esxfcaliases :
        print "no zone name %s_%s vsan %s" % (esxfcalias, NAfcalias, vsan)

