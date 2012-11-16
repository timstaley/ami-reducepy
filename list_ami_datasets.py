"""
Groups AMI datasets by pointing direction,
then dumps them in JSON format.
"""

import ami
import json

ami_rootdir = '/opt/ami'

r = ami.Reduce(ami_rootdir)
named_groups = r.group_pointings()
json.dump(named_groups, open('groups.json', 'w'),
          sort_keys=True, indent=4)


