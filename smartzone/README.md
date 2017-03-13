# SmartZone

   The script generates zoning commands suitable for Cisco MDS switches
   running NX-OS by examining existing params entries and using pattern
   matching aginst a provided configuration file containing hostnames,
   pwwns and SmartZones.

## gen_smartzones.py

```
usage: gen_smartzones.py [-h] -c CONFIG_HOSTS --vsan VSAN --zoneset ZONESET -f
                         {impar,par} [--check] [-s SWITCH] [-u USERNAME]
                         [-p PASSWORD] [--use_keys] [--key_file KEY_FILE]
gen_smartzones.py: error: argument -c/--config_hosts is required
esquizophrenia:python-mdszoning italosantos$ ./smartzone/gen_smartzones.py -h
usage: gen_smartzones.py [-h] -c CONFIG_HOSTS --vsan VSAN --zoneset ZONESET -f
                         {impar,par} [--check] [-s SWITCH] [-u USERNAME]
                         [-p PASSWORD] [--use_keys] [--key_file KEY_FILE]

Generate SmartZone commands from input config file listing of short hostnames,
pwwns and zones which each host will belongs.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG_HOSTS, --config_hosts CONFIG_HOSTS
                        Configuration file with hosts, pwwns and zones
  --vsan VSAN           VSAN ID
  --zoneset ZONESET     ZoneSet name
  -f {impar,par}, --fabric {impar,par}
                        Fabric side
  --check               [optional] Start a validation process by connection on
                        MDS switch of all params
  -s SWITCH, --switch SWITCH
                        MDS switch fqdn or IP
  -u USERNAME, --username USERNAME
                        [optional] Username to ssh into mds switch. Alternate:
                        set environment variable MDS_USERNAME. If neither
                        exists, defaults to current OS username
  -p PASSWORD, --password PASSWORD
                        [optional] Password to ssh into mds switch. Alternate:
                        set environment variable MDS_PASSWORD. If unset
                        use_keys defaults to True.
  --use_keys            [optional] Use ssh keys to log into switch. If set key
                        file will need be pass as param
  --key_file KEY_FILE   [optional] filename for ssh key file
```

> **note**: This script currently read the params from the `--config_hosts` argument
and validate all into the MDS if the argument `--check` was passed. The output file
should be saved via redirection eg. `> output_zoning.txt` could simply be reviewed
and cut and pasted into the relevant switch.