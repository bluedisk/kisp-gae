# -*- coding:utf-8 -*-

######################################
#
# Wholook Transport Layer Security
#
import requests
import json

from core.models import SMSLog


def sendSMS(msg,caller,callees):

    url = 'http://donutnamoo.com/api/wholook.php'

    callee = callees
    if type(callees) == list or type(callees) == tuple:
        callee = ",".join(callees)
    
    data = {'cert' : 'wholookwholookwholoolook',
              'msg' : msg,
              'from' : caller,
              'to': callee,
              'etc': 'kisp' }

    response = requests.post(url, data=data)
    
    result = response.text
    result = json.loads(result)
    
    if result['result'] == 0:
        log = SMSLog()
        log.count = result['count']
        log.caller = caller
        log.callee = callee
        log.msg = msg
        log.save()

        return log.count

    return 0