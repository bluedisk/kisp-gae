import re

def strip_number(cell):
    return re.sub('[^0-9]','',cell)

def format_cell(cell):
    cell = strip_number(cell)
    mid_cnt = len(cell)-7
    return "%s-%s-%s"%(cell[:3],cell[3:3+mid_cnt],cell[-4:])

def format_regnum(regnum):
    regnum = strip_number(regnum)
    return "%s-%s"%(regnum[:6], regnum[6:])
