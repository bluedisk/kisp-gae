# -*- coding: utf-8 -*-

from message.push.apns import APNs,Payload
from message.push.pygcm.manage import GCMManager
from message.push.certs.settings import *

apns_conn = None
gcm_conn = None


def push_to(token, text, count):
    if token.os == 'android':
        push_to_gcm(token.token, text, count)
    else:
        push_to_apns(token.token, text, count)

def push_to_gcm(keys, text, count):

    successed = []
    failed = []

    global gcm_conn
    if not gcm_conn:
        gcm_conn = GCMManager(GCM_KEY)

    gcm_conn.send(keys,text)


def push_to_apns(keys, text, count):
    successed = []
    failed = []

    global apns_conn
    if not apns_conn:
        apns_conn = APNs(use_sandbox=APNS_SANDBOX, cert_file=APNS_CERT, key_file=APNS_CERT)

    payload = Payload(alert=text, sound="default", badge=count)

    for key in keys:
        apns_conn.gateway_server.send(key, payload)
        

