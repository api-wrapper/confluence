#!/usr/bin/env python3
"""Remove archived spaces matching specific description"""
from confluence_api import Spaces

spaces = Spaces()
review = spaces.get(s_type='global', status='archived',
                    expand='description.plain') # related with 'desc' variable

pattern = 'allowed to remove'
removed = 0

print(F'Will be checked {len(review)} spaces')
print(F'Will be removed spaces with pattern "{pattern}" found in description')

for space in review:
    key = space['key']
    name = space['name']
    desc = space['description']['plain']['value']

    if pattern in desc:
        print(F'Removing the space {key} ({name})...', end =" ", flush=True)
        # spaces.delete(key) # uncomment if you really want to execute the task
        print('Removed', flush=True)
        removed += 1

print(F'Removed {removed} spaces')
