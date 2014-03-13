#!/usr/bin/env python
import os
import sys
import json

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kispapp.settings")


    from core.models import ContactGroup, ContactItem

f = open('kisp.json','rt')
json_data = f.read()

json_data = json.loads(json_data)

for group, items in json_data.items():
    group_obj = ContactGroup()
    group_obj.name = group
    group_obj.save()
    for item in items:
        item_obj = ContactItem()
        item_obj.name = item['name']
        item_obj.cell = item['cell']
        item_obj.group = group_obj
        item_obj.save()
