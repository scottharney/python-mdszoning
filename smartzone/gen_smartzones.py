#!/usr/bin/python
# gen_smartzones.py - Italo Santos <italux.santos@gmail.com>

import os
import sys
import getpass
sys.path.append("./library")
import argparse
import ConfigParser
from utils import *
from na_funcs import *
from cisco_funcs import *

def check_on_switch(mds, zoneset, zones, vsan, fabric, switch):

    non_existent_zones = []
    zoneset_existent = False

    # http://www.cisco.com/c/en/us/td/docs/switches/datacenter/mds9000/sw/6_2/configuration/guides/config_limits/b_mds_9000_configuration_limits_6_2.html
    # Table 2 Fabric-level Fibre Channel Configuration Limits
    # Note: The preferred number of members per zone is 2, and the maximum recommended limit is 50.
    smartzone_members_limit = 50

    print bcolors.OKGREEN + "Initiate validations ...\n" + bcolors.ENDC
    print bcolors.BOLD + "Validating ZoneSet %s and VSAN ID %s on MDS..." % (zoneset, vsan) + bcolors.ENDC
    if zoneset_exists(mds, zoneset, vsan) is not False:
        zoneset_existent = True

    for zone_name in zones.keys():
        if len(zone_name) > 1:
            print bcolors.BOLD + "Validating %s on MDS..." % zone_name.strip() + bcolors.ENDC
            if zone_exists(mds, zone_name, vsan) is False:
                non_existent_zones.append(zone_name)

        print bcolors.BOLD + "Validating number of members of %s on MDS..." % zone_name.strip() + bcolors.ENDC
        members = count_smartzone_members(mds, zone_name)

    if zoneset_existent is False or len(non_existent_zones) > 0 or members >= smartzone_members_limit:
        print bcolors.WARNING + "\n### ATENTION! Validation found some errors ... ###\n" + bcolors.ENDC

        if zoneset_existent is False:
            print bcolors.FAIL + "ZoneSet \"%s\" and/or VSAN ID %s doesn't exists!\n" % (zoneset, vsan) + bcolors.ENDC

        if len(non_existent_zones) > 0:
            for zone in non_existent_zones:
                print bcolors.FAIL + "Zone \"%s\" doesn't exists!" % zone.strip() + bcolors.ENDC

        if members >= smartzone_members_limit:
            print bcolors.FAIL + "Zone \"%s\" has more then 50 members\n" % zone_name.strip() + bcolors.ENDC
        
        if confirm("Are you sure you want to continue?"):
            generate_smartzones(config_file, zoneset, vsan, fabric, switch)
    else:
        print bcolors.OKGREEN + "\nValidation successfully!" + bcolors.ENDC
        generate_smartzones(config_file, zoneset, vsan, fabric, switch)   

def generate_smartzones(config_file, zoneset, vsan, fabric, switch=None, check=False, mds=None):

    try:
        config = ConfigParser.ConfigParser()
        config.read(config_file)
    except Exception, e:
        print bcolors.FAIL + "Error reading config file!" + bcolors.ENDC
        print bcolors.BOLD + "Exception:" + bcolors.ENDC + "\n%s" % e
        exit(1)

    hosts_per_zone = {}

    for host in config.sections():
        for zone in config.get(host, 'zones').split(','):
            hosts_per_zone[zone] = []

    for host in config.sections():
        for zone in config.get(host, 'zones').split(','):
            hosts_per_zone[zone].append(host)

    if check:
        check_on_switch(mds, zoneset, hosts_per_zone, vsan, fabric, switch)
    else:
        if switch:
            print bcolors.OKGREEN + "\nGenerating commands to switch %s ... \n" % switch + bcolors.ENDC
        else:
            print bcolors.OKGREEN + "\nGenerating commands to FABRIC %s ... \n" % fabric + bcolors.ENDC
        print "config t"
        print "device-alias database"
        for host in config.sections():
            print "  device-alias name %s pwwn %s" % (host.strip(), config.get(host, fabric))
        print "device-alias commit\n"

        for zone, hosts in hosts_per_zone.iteritems():
            if len(zone) > 1:
                print "zone name %s vsan %s" % (zone.strip(), vsan)
                for host in hosts:
                    print "  member device-alias %s initiator" % host.strip()
                print "exit\n"

        print "zoneset activate name %s vsan %s\n" % (zoneset, vsan)

        print "copy running-config startup-config\n"

if __name__ == "__main__":

    arguments = argparse.ArgumentParser(
        description='Generate SmartZone commands from input config file listing of short hostnames, pwwns and zones which each host will belongs.')
    arguments.add_argument(
        '-c','--config_hosts', required=True, type=str,
        help='Configuration file with hosts, pwwns and zones')
    arguments.add_argument(
        '--vsan', required=True, type=str,
        help='VSAN ID')
    arguments.add_argument(
        '--zoneset', required=True, type=str,
        help='ZoneSet name')
    arguments.add_argument(
        '-f','--fabric', required=True, type=str, choices=['impar', 'par'],
        help='Fabric side')
    arguments.add_argument(
        '--check',default=False, action='store_true',
        help='[optional] Start a validation process by connection on MDS switch of all params')
    arguments.add_argument(
        '-s','--switch', required=False, type=str,
        help='MDS switch fqdn or IP')
    arguments.add_argument(
        '-u','--username', required=False, type=str,
        help='[optional] Username to ssh into mds switch. Alternate: set environment variable MDS_USERNAME. If neither exists, defaults to current OS username') 
    arguments.add_argument(
        '-p','--password', required=False, type=str,
        help='[optional] Password to ssh into mds switch. Alternate: set environment variable MDS_PASSWORD. If unset use_keys defaults to True.') 
    arguments.add_argument(
        '--use_keys', required=False, action='store_true',
        help='[optional] Use ssh keys to log into switch. If set key file will need be pass as param') 
    arguments.add_argument(
        '--key_file', required=False, type=str, 
        help='[optional] filename for ssh key file')

    args = arguments.parse_args()

    config_file = args.config_hosts

    if not os.path.exists(config_file):
        print bcolors.FAIL + "%s: No such file or directory!" % config_file + bcolors.ENDC
        exit(1)

    vsan = args.vsan
    zoneset = args.zoneset
    fabric = args.fabric
    switch = None

    if args.check:
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

        switch = args.switch

        # Params to connect on MDS
        mds = {
            'device_type': 'cisco_nxos',
            'ip': switch,
            'verbose': False,
            'username': username,
            'password': password,
            'use_keys': use_keys
        }
        generate_smartzones(config_file, zoneset, vsan, fabric, switch=switch, check=True, mds=mds)
    else:
        generate_smartzones(config_file, zoneset, vsan, fabric)

