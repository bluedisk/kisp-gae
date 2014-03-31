"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

from django.http import HttpResponseRedirect, HttpResponse
from datetime import datetime, timedelta, date, tzinfo
from kispapp.settings import TIME_ZONE
import pytz

class EST(tzinfo):
    def utcoffset(self, dt):
      return datetime.timedelta(hours=-5)

    def dst(self, dt):
        return datetime.timedelta(0)

def timezone(request):
    tzinfo = pytz.timezone(TIME_ZONE)
    aware2 = tzinfo.localize(datetime.now())

    aware = datetime.now().replace(tzinfo=tzinfo)
    typ_now = datetime.now()
    return HttpResponse("now:%s<BR>today:%s<BR>aware:%s<BR>aware2:%s<BR>"%(typ_now,'',aware,aware2))