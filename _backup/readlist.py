
f = open('kisp.list','rt')



FIELD_NAME = ('group', 'name', 'cell', 'etc1', 'etc2', 'sp1', 'sp2', 'sp3', 'sp4') 

alldata = {}

index=99
item={}
for line in f:
    if index >= 9:
        if 'name' in item:
            group = item['group']

            if not group in alldata:
                alldata[group] = []
            
            alldata[group].append(item)

        index = 0
        item = {}

    field = FIELD_NAME[index]
    value = line.strip()
    index = index + 1

    item[field] = value

for group,items in alldata.items():
    print "%s : %s"%(group, len(items))

import json

print json.dumps(alldata)