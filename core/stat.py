# -*- coding: utf-8 -*-
from core.models import Point

def stat():
    list = {}
    for p in Point.objects.all():
        key = "%s:%s" % (p.name, p.regnum)
        if key in list:
            list[key] += p.amount
        else:
            list[key] = p.amount

    for key in sorted(list):
        print "%s : %d" % (key, list[key])

