# -*- coding:utf-8 -*-
from datetime import date
from xlwt import Workbook, easyxf

import cStringIO
import urllib

from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from core.models import Event, Entry


@login_required
def agent(request, eid):
    if not request.user.is_staff:
        raise PermissionDenied

    event = Event.objects.get(id=eid)
    entries = Entry.objects.filter(event=event)

    book = Workbook()
    sheet = book.add_sheet(u'참가자 명단')

    style = easyxf(
        'pattern: pattern solid, fore_colour 0x2f;'
        'align: vertical center, horizontal center;'
        'borders: left no_line,, right no_line,, top no_line,, bottom thick;'
        'font: bold true, height 300;'
    )

    sheet.write_merge(0, 0, 0, 7, u'%s 마라톤 패트롤 명단' % event.title, style)

    style_lt = easyxf(
        'borders: left thick, right thin, top thick, bottom thin;'
        'pattern: pattern solid, fore_colour 0x2f;'
        'font: bold true;'
        'align: horizontal center;'
    )
    style_mt = easyxf(
        'borders: left thin, right thin, top thick, bottom thin;'
        'pattern: pattern solid, fore_colour 0x2f;'
        'font: bold true;'
        'align: horizontal center;'
    )
    style_rt = easyxf(
        'borders: left thin, right thick, top thick, bottom thin;'
        'pattern: pattern solid, fore_colour 0x2f;'
        'font: bold true;'
        'align: horizontal center;'
    )
    style_lm = easyxf(
        'borders: left thick, right thin, top thin, bottom thin;'
        'align: horizontal center;'
    )
    style_mm = easyxf(
        'borders: left thin, right thin, top thin, bottom thin;'
        'align: horizontal center;'
    )
    style_rm = easyxf(
        'borders: left thin, right thick, top thin, bottom thin;'
        'align: horizontal center;'
    )
    style_b = easyxf(
        'borders: top thick;'
    )

    style_lb = easyxf(
        'borders: left thick, right thin, top thick, bottom thick;'
        'pattern: pattern solid, fore_colour 0x2c;'
        'align: horizontal center;'
    )
    style_rb = easyxf(
        'borders: left thin, right thick, top thick, bottom thick;'
        'pattern: pattern solid, fore_colour 0x2c;'
        'align: horizontal center;'
    )

    sheet.col(0).width = 2000
    sheet.col(1).width = 4000
    sheet.col(2).width = 5000
    sheet.col(3).width = 2000
    sheet.col(4).width = 3000
    sheet.col(5).width = 8000
    sheet.col(6).width = 6000
    sheet.col(7).width = 2000

    # write agent table
    row = 1
    sheet.write(row, 0, u'이름', style_lt)
    sheet.write(row, 1, u'연락처', style_mt)
    sheet.write(row, 2, u'주민번호', style_mt)
    sheet.write(row, 3, u'사이즈', style_mt)
    sheet.write(row, 4, u'희망거리', style_mt)
    sheet.write(row, 5, u'스킬', style_mt)
    sheet.write(row, 6, u'비고', style_mt)
    sheet.write(row, 7, u'조장가능', style_rt)

    size_count = {}

    row = row + 1
    for entry in entries:
        sheet.write(row, 0, entry.name, style_lm)
        sheet.write(row, 1, entry.cell, style_mm)
        sheet.write(row, 2, entry.regnum, style_mm)
        sheet.write(row, 3, entry.tsize, style_mm)
        sheet.write(row, 4, entry.get_hdist_display(), style_mm)
        sheet.write(row, 5, entry.skill_display(), style_mm)
        sheet.write(row, 6, entry.etc, style_mm)
        sheet.write(row, 7, '', style_rm)

        if not entry.tsize in size_count:
            size_count[entry.tsize] = 1
        else:
            size_count[entry.tsize] = size_count[entry.tsize] + 1
        row = row + 1

    for col in range(8):
        sheet.write(row, col, '', style_b)

    # write size table
    row = 2
    sheet.write(2, 9, u'사이즈', style_lt)
    sheet.write(2, 10, u'수량', style_rt)

    row = row + 1
    for size, count in size_count.items():
        sheet.write(row, 9, size, style_lm)
        sheet.write(row, 10, count, style_rm)
        row = row + 1

    sheet.write(row, 9, '', style_lb)
    sheet.write(row, 10, len(entries), style_rb)

    output = cStringIO.StringIO()
    book.save(output)

    response = HttpResponse(output.getvalue(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = u'attachment; filename="%s.xls"' % (urllib.quote(event.short_title.encode('utf-8')))

    return response
