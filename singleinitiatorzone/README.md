# Single Initiator Zone

   The first script generates zoning commands suitable for Cisco MDS switches
   running NX-OS by examining existing fcalias entries and using pattern
   matching aginst a provided list of hostnames.  The use case here is a SAN
   migration to a new target array, in my particular initial case a NetApp
   cDOT cluster.  This may work on other Cisco NX-OS devices for fiber channel
   with minimal modifications.  The reliance here is existing fcalias entries
   that contain server hostnames and therefore can be matched against with
   case-insenstive regexes.

## List of Scripts

  - [genzonesfromexistingfcaliases.py](.genzonesfromexistingfcaliases.py)
  - [checkwwpnigroupfcaliases.py](.checkwwpnigroupfcaliases.py)
  - [initiatorscheck.py](.initiatorscheck.py)

## genzonesfromexistingfcaliases.py

```
usage: genzonesfromexistingfcaliases.py [-h] --hostname HOSTNAME
                                        --hosts_filename HOSTS_FILENAME --vsan
                                        VSAN --zoneset ZONESET
                                        [--fcalias_filename FCALIAS_FILENAME]
                                        [--target_fcalias TARGET_FCALIAS]
                                        [--username USERNAME]
                                        [--get_from_switch]
                                        [--password PASSWORD] [--use_keys]
                                        [--backout] [--key_file KEY_FILE]

Generate zoning commands from input file listing of short hostnames one per
line. Will match against switch fcalias entries by hostname pattern. print to
STDOUT. redirect with > filename.txt

optional arguments:
  -h, --help            show this help message and exit
  --hostname HOSTNAME   MDS switch fqdn or IP.
  --hosts_filename HOSTS_FILENAME
                        list of hosts to match against. one per line
  --vsan VSAN           VSAN for fcaliases/zones
  --zoneset ZONESET     zoneset name
  --fcalias_filename FCALIAS_FILENAME
                        generated fcaliases output from 'ssh
                        username@switchname show fcalias >
                        switch_fcaliases.txt'
  --target_fcalias TARGET_FCALIAS
                        optional fcalias name of cDOT cluster on switch.
                        default ='NAC1'
  --username USERNAME   optional username to ssh into mds switch. Alternate:
                        set environment variable MDS_USERNAME. If neither
                        exists, defaults to current OS username
  --get_from_switch     get fcaliases directly from switch instead of file.
                        NOTE: not yet implemented
  --password PASSWORD   optional password to ssh into mds switch. Alternate:
                        set environment variable MDS_PASSWORD. If unset
                        use_keys defaults to True.
  --use_keys            use ssh keys to log into switch
  --backout             generate backout commands
  --key_file KEY_FILE   filename for ssh key file
```

> **note**: This script currently relies on the `--fcalias_filename` argument
and that the functionality to pull fcalias data directly from the switch is
not yet implemented as of 2015-12-17.  The output file save via redirection eg.
`> output_zoning.txt` could simply be reviewed and cut and pasted into the
relevant switch. 

## initiatorscheck.py | checkwwpnigroupfcaliases.py
  These scripts perform checks that zoning items are as
  expected. Note that they also require the NetApp Manageability SDK which is
  for now behind support.netapp.com and requires a netapp login.  The first
  script is a comparison of NetApp igroup member WWPNs and fcaliases on the
  switch.  It's a post-check for some of the work here.  The second script is
  just a sanity check against a filer only for initiators that are logged in
  (zoned) but have no igroup membership.   
