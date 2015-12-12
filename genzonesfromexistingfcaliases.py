#!/usr/bin/python
# genzonesfromexistingfcaliases.py
#
# generate zoning commands given output of "show fcalias" from switch
# assumes zones have lowercase entries and single initiator zoning is used
# generates zoning commands to add new array.  List of hostnames should
# also be provided one per line in a file.
# populate relevant variables below


mds = "jdc-mds1.prod.entergy.com"
fcalias_filename = "jdcmds1_sh_fcalias.txt" # ssh $mds 'sh fcalias > $fcalias_filename before
hostname_filename = "hostlist.txt"
NAfcalias = "NAC1"
vsan = "101"
zoneset = "ZS_JDCUPMDS1"

hostnames = open(hostname_filename, "r").readlines()
fcaliases = open(fcalias_filename, "r").readlines()

esxfcaliases = []
zones = []
for host in hostnames :
    checkhost = host.lower().strip()
    for fcalias in fcaliases:
        if checkhost in fcalias :
            esxhost = fcalias.split()
            esxfcaliases.append(esxhost[2])
            zones.append("%s_%s" % (esxhost[2], NAfcalias))
        
    
for esxfcalias in esxfcaliases :
    print "\nzone name %s_%s vsan %s" % (esxfcalias, NAfcalias, vsan)
    print "   member fcalias %s" % NAfcalias
    print "   member fcalias %s" % esxfcalias
    

print "\n"
print "zoneset name %s vsan %s" % (zoneset, vsan)
for zone in zones :
    print "   member %s" % zone
    

