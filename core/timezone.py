from django.http import HttpResponse
from datetime import datetime
from kispapp.settings import TIME_ZONE
import pytz

def now():
    now = datetime.now().replace(tzinfo=pytz.utc)
    aware = now.astimezone(pytz.timezone(TIME_ZONE))

    return aware

def today():
    return now().date()

def test(request):
    return HttpResponse(now())