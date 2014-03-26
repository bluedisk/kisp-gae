import re

def strip_cell(cell):
    return re.sub('[^0-9]','',cell)

def format_cell(cell):
    cell = strip_cell(cell)
    mid_cnt = len(cell)-7
    return "%s-%s-%s"%(cell[:3],cell[3:3+mid_cnt],cell[-4:])