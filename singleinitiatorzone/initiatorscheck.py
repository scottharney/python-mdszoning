#!/usr/bin/python
# initiatorscheck.py
#
# check fcp initatior show on a filer for logged in initiators with no
# igroup members or multiple igroup members

import sys
import argparse
import json
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
    description='Get connected fcp initiators from cDOT filer and check that they are mapped to an igroup and also not mapped to multiple igroups ')
arguments.add_argument(
    '--filer_hostname', required=True, type=str,
    help='filer fqdn or IP')
arguments.add_argument(
    '--filer_username', required=False, type=str,
    help='optional username to ssh into mds switch. Alternate: set environment variable FILER_USERNAME. If neither exists, defaults to admin') 
arguments.add_argument(
    '--filer_password', required=False, type=str,
    help='optional password to ssh into mds switch. Alternate: set environment variable filer_PASSWORD. If unset use_keys defaults to True.') 
arguments.add_argument(
    '--svm', '--vserver', required=False, type=str,
    help='limit "fcp initiator show" query named netapp vserver')
arguments.add_argument(
    '--lif', '--adapter', required=False, type=str,
    help='limit "fcp initiator show" query to named netapp vserver lif')

args = arguments.parse_args()

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

if args.svm :
    svm = args.svm
else :
    svm = False

if args.lif :
    lif = args.lif
else:
    lif = False
    
filer_hostname = args.filer_hostname

# main loop
pp = pprint.PrettyPrinter(indent=4)

filerconnect = cdotconnect(filer_hostname,filer_username,filer_password)

api = NaElement("fcp-initiator-get-iter")
## can stack elements on to the query to limit output
xi = NaElement("query")
api.child_add(xi)
xi1 = NaElement("fcp-adapter-initiators-info")
xi.child_add(xi1)
if svm :
    xi1.child_add_string("vserver",svm)
if lif :
    xi1.child_add_string("adapter",lif)

xo = filerconnect.invoke_elem(api)
if (xo.results_status() == "failed") :
    print ("Error:\n")
    print (xo.sprintf())
    sys.exit (1)

if debug :
    print xo.sprintf() #debugging

initiators_list = []

initiators_list = getfcpinitiators(xo)
i = 1
for item in range(len(initiators_list)) :
    if i > len(initiators_list) :
        break # leave the loop when iterator > length of our list
    x = 0
    for initiators in range(len(initiators_list[i])) :
        if len(initiators_list[i][x]['igroups']) > 1 :
            print "[ { 'results' : 'multiple igroups found'},"
            print "[ %s," % initiators_list[i-1]
            print "    [ %s ] ]" % initiators_list[i][x]
        elif initiators_list[i][x]['igroups'][0]['igroup'] == None :
            print "[ { 'results' : 'no igroup found'},"
            print "[ %s," % initiators_list[i-1]
            print "    [ %s ] ] ]" % initiators_list[i][x]
        x = x+1
    i = i+2


    
if debug :
    print(json.dumps(initiators_list, indent=2, sort_keys=True))


