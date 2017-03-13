# Python scripts to automate MDS fibre channel zoning

  Fibre channel zoning is a challenge for storage admins and a time sink and,
  automation helps reduce the potential for human error. This scripts will help 
  generate and push out zoning changes.

  > **IMPORTANT**: The multidue of objects, lengthy names and WWPNs require standardization.

## Requirements

  - [Python 2.7+](https://www.python.org/download/releases/2.7/)
  - [NetrMiko](https://github.com/ktbyers/netmiko) and it's dependencies
  - [CiscoConfParse](https://github.com/mpenning/ciscoconfparse) and it's dependencies

## Documentation

  - [Single Initiator](singleinitiatorzone/README.md)
  - [SmartZone](smartzone/README.md)
