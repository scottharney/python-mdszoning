# na_funcs.py
#
# helper functions for netapp cdot filers
# uses netapp managability sdk

import sys
sys.path.append("/home/sharney/source/netapp-manageability-sdk-5.2.2/lib/python/NetApp")
try:
    from NaServer import *
    has_nasdk = True
except:
    has_nasdk = False    

    
if not has_nasdk :
    print "NetApp managability SDK 5.2 or higher is required to use this script. download"
    print "installation from: https://support.netapp.com"
    exit(1)
    

    
def cdotconnect(filer, username, password) :
    """ return a filer connection handle """
    s = NaServer(filer, 1 , 31)
    s.set_server_type("FILER")
    s.set_transport_type("HTTP") # would like to use HTTPS but I get ssl cert errors on Ubuntu 15.x
    s.set_port(80)
    s.set_style("LOGIN")
    s.set_admin_user(username, password)
    return s


def getigroupwwpns(igroupname, filerconnection) :
    """ given an igroup name and connection handle, return normalized
    list of initiators in that igroup from cDOT filer
    """
    api = NaElement("igroup-get-iter")
    query = NaElement("query")
    api.child_add(query)
    
    initiator_group_info = NaElement("initiator-group-info")
    query.child_add(initiator_group_info)
    
    initiator_group_info.child_add_string("initiator-group-name",igroupname)
    
    xo = filerconnection.invoke_elem(api)
    if (xo.results_status() == "failed") :
        print ("Error:\n")
        print (xo.sprintf())
        sys.exit (1)
        
    attributes = xo.child_get("attributes-list")
    initiator_group_info = attributes.child_get("initiator-group-info")
    initiators = initiator_group_info.child_get("initiators").children_get()
    
    items = []
    for igroup in initiators :
        item = igroup.child_get_string("initiator-name")
        items.append(item) 
        
    return items



def getigrouplist(NaElement) :
    ''' return a list of igroup dictionaries'''
    igroup_list = []

    for igroups in NaElement.children_get() :
        initiator_dict = {}
        igroup = ''
        igroup = igroups.child_get_string('initiator-group-name')
        initiator_dict['igroup'] = igroup
        igroup_list.append(initiator_dict)

    return (igroup_list)
            
            
def getfcpconnectedinitiators(NaElement) :
    ''' return a list of connected fcp initiators'''

    connected_initiators_list = []
    
    for getitem in NaElement.children_get() :
        initiator_dict = {}
        try:
            igroup_list = getigrouplist(getitem.child_get('initiator-group-list'))
        except:
            igroup_list = [{'igroup': None}]
        initiator_dict['igroups'] = igroup_list
        initiator_dict['wwpn'] = getitem.child_get_string('port-name')
        connected_initiators_list.append(initiator_dict)
        
    return (connected_initiators_list)


def getfcpinitiators(NaElement) :
    ''' return a list of dicts containing connected fcp initiator information '''

    initiators_list =[]
    
    for getitem in NaElement.child_get('attributes-list').children_get() :
        vserver_adapter_dict = {} 
        connected_initiators_list = []
        vserver_adapter_dict['vserver'] = getitem.child_get_string('vserver')
        vserver_adapter_dict['adapter'] = getitem.child_get_string('adapter')
        initiators_list.append(vserver_adapter_dict)
        connected_initiators_list = getfcpconnectedinitiators(getitem.child_get('fcp-connected-initiators'))
        initiators_list.append(connected_initiators_list)
        
    return (initiators_list)
