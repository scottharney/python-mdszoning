# cisco_funcs.py
#
# helper functions for mds switches
# uses netmiko and ciscoconfparse


try:
    from netmiko import ConnectHandler
    has_netmiko = True
except:
    has_netmiko = False
try:
    from ciscoconfparse import CiscoConfParse
    has_ciscoconfparse = True
except:
    has_ciscoconfparse = False

if not has_netmiko :
    print "netmiko is required to use this script, download installation from:"
    print "https://github.com/ktbyers/netmiko/tree/master/netmiko"
    exit(1)

if not has_ciscoconfparse :
    print "The ciscoconfparse module is needed. Download "
    print "installation from: https://github.com/mpenning/ciscoconfparse"
    exit(1)


def parsefcaliases(cisco_cfg) :
    """ parse fcalias data from cisco show running-config into list of dictionaries """
    fcalias_dict = {}
    fcaliases = cisco_cfg.find_objects(r"^fcalias name")
    for fcalias_line in fcaliases :
        fcalias_line_list = fcalias_line.text.strip().split()
        curfcalias = fcalias_line_list[2]
        fcalias_dict[curfcalias] = {}
        curfcalias_dict = {}
        curfcalias_dict['name'] = curfcalias
        curfcalias_dict['vsan'] = fcalias_line_list[4]
        pwwn_list = []
        for members_line in fcalias_line.children :
            members_line_list = members_line.text.strip().split()
            pwwn_list.append(members_line_list[2])
            curfcalias_dict['pwwns'] = pwwn_list
        if pwwn_list == [] :
            curfcalias_dict['pwwns'] = []
        fcalias_dict[curfcalias] = curfcalias_dict

    return(fcalias_dict)


def nonblank_lines(f):
    for l in f:
        line = l.strip()
        if line:
            yield line


def handle_mds_continue(net_connect, cmd):
    net_connect.remote_conn.sendall(cmd)
    time.sleep(1)
    output = net_connect.remote_conn.recv(65535).decode('utf-8')       
    if 'want to continue' in output:
        net_connect.remote_conn.sendall('y\n')
        output += net_connect.remote_conn.recv(65535).decode('utf-8')
        return output   



def getzones(sh_zones) :
    ''' get a list of zone dictionies and their memberchildren in lists of dictionaries'''
    zones = sh_zones.find_objects(r"zone name")
    zones_list = []
    for zone in zones :
        zone_list = []
        zoneline_dict = {}
        zoneline = zone.text.strip().split()
        zoneline_dict['vsan'] = zoneline[4]
        zoneline_dict['name'] = zoneline[2]
        zone_list.append(zoneline_dict)
        for fcalias in zone.children :
            fcaliases = []
            fcaliasline = fcalias.text.strip().split()
            fcaliasline_dict = {}
            try:
                fcaliasline_dict['fcalias'] = fcaliasline[2]
            except:
                fcaliasline_dict['fcalias'] = None
            fcaliases.append(fcaliasline_dict)
            for member in fcalias.children:
                members = []
                memberline = member.text.strip().split()
                memberline_dict = {}
                memberline_dict['pwwn'] = memberline[1]
                members.append(memberline_dict)
                fcaliases.append(members)
            zone_list.append(fcaliases)
        zones_list.append(zone_list)
            
    return(zones_list)
            

