# -*- coding:utf-8 -*-
from datetime import date
from xlwt import Workbook, easyxf
from io import BytesIO

entries = [
{'name':u'이효섭', 'regnum': '740410-1018712', 'tsize': 95 },
{'name':u'강영철', 'regnum': '750217-1155717', 'tsize': 105},
{'name':u'박철수', 'regnum': '780106-1221227', 'tsize': 110},
]

book = Workbook()
sheet = book.add_sheet(u'참자가 명단')

style = easyxf(
 'pattern: pattern solid, fore_colour 0x2f;'
 'align: vertical center, horizontal center;'
 'borders: left no_line,, right no_line,, top no_line,, bottom thick;'
 'font: bold true, height 400;'
 )

sheet.write_merge(0,0,0,4,u'title',style)

sheet.col(0).width = 3000
sheet.col(1).width = 8000
sheet.col(2).width = 2000
sheet.col(3).width = 6000
sheet.col(4).width = 3000

style_lt = easyxf(
 'borders: left thick, right thin, top thick, bottom thin;'
 'pattern: pattern solid, fore_colour 0x2f',
 )
style_mt = easyxf(
 'borders: left thin, right thin, top thick, bottom thin;'
 'pattern: pattern solid, fore_colour 0x2f',
 )
style_rt = easyxf(
 'borders: left thin, right thick, top thick, bottom thin;'
 'pattern: pattern solid, fore_colour 0x2f',
 )
style_lm = easyxf(
 'borders: left thick, right thin, top thin, bottom thin;'
 )
style_mm = easyxf(
 'borders: left thin, right thin, top thin, bottom thin;'
 )
style_rm = easyxf(
 'borders: left thin, right thick, top thin, bottom thin;'
 )
style_b = easyxf(
 'borders: top thick;'
 )

style_lb = easyxf(
 'borders: left thick, right thin, top thick, bottom thick;'
 'pattern: pattern solid, fore_colour 0x2c',
 )
style_rb = easyxf(
 'borders: left thin, right thick, top thick, bottom thick;'
 'pattern: pattern solid, fore_colour 0x2c',
 )

# write agent table
sheet.write(1,0,u'이름',style_lt)
sheet.write(1,1,u'주민번호',style_mt)
sheet.write(1,2,u'사이즈',style_mt)
sheet.write(1,3,u'비고',style_mt)
sheet.write(1,4,u'조장가능',style_rt)

size_count = {90:0,95:0,100:0,105:0,110:0}

idx=2
for entry in entries:
    sheet.write(idx,0, entry['name'],style_lm)
    sheet.write(idx,1, entry['regnum'],style_mm)
    sheet.write(idx,2, entry['tsize'],style_mm)
    sheet.write(idx,3, '',style_mm)
    sheet.write(idx,4, '',style_rm)
    size_count[entry['tsize']] = size_count[entry['tsize']] + 1
    idx = idx + 1

sheet.write(idx,0, '',style_b)
sheet.write(idx,1, '',style_b)
sheet.write(idx,2, '',style_b)
sheet.write(idx,3, '',style_b)
sheet.write(idx,4, '',style_b)

# write size table
sheet.write(2,6,u'사이즈',style_lt)
sheet.write(2,7,u'수량',style_rt)

size_idx = 3
for size, count in size_count.items():
    sheet.write(size_idx,6,size,style_lm)
    sheet.write(size_idx,7,count,style_rm)
    size_idx = size_idx + 1

sheet.write(size_idx,6,'',style_lb)
sheet.write(size_idx,7,len(entries),style_rb)

target = BytesIO()
book.save(target)
