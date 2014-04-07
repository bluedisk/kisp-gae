# -*- coding:utf-8 -*-
from django.http import HttpResponse
from django.db import transaction

from message import models
from message.targets import Target, TargetFactory
from message.interface import DjangoMessageInterface

@transaction.atomic
def worker():

    msgs = DjangoMessageInterface.query_message()

    sms = []
    gcm = []
    apns = []
    failed = []

    for msg in msgs:
        uri = DjangoMessageInterface.get_uri(msg)
        targets = targets.TargetFactory.from_uri(uri)

        for target in targets:
            if target.type == u'sms':
                sms.append(target)
            elif target.type == u'push':
                if target.model == u'gcm':
                    gcm.append(target)
                else:
                    apns.append(target)
            else:
                failed.append(target)


        send_apns_target(msg.msg, apns)


def send_apns_target(msg, targets):
    apns_conn = APNs(use_sandbox=APNS_SANDBOX, cert_file=APNS_CERT, key_file=APNS_CERT)

    keys = TargetFactory.from_uri(targets)

    for key in keys:
        payload = Payload(alert=msg, sound="default", badge=key.fragment or 1)
        apns_conn.gateway_server.send(key.username, payload)


def send_gcm_target(msg, targets):
    gcm_conn = GCMManager(GCM_KEY)

    keys = TargetFactory.from_uri(targets)

    for key in keys:
        gcm_conn.send(key.username,msg)


def send_sms_target(msg, targets):
    

    

def worker_view(request):
    result = worker()
    return HttpResponse(result)

