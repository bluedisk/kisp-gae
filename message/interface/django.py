# -*- coding:utf-8 -*-
from datetime import datetime
from django.db import models
from gettext import gettext as _

from message import workers

from django.contrib.auth import get_user_model
User = get_user_model()

class Message(models.Model):
    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')

    def __unicode__(self):
        return "%s => %s"%(sender, target)

    sender = models.CharField(_('sender id'), max_length=1024)
    target = models.CharField(_('target uri'),max_length=1024)

    created_at = models.DateTimeField(_('created time'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated time'), auto_now=True)
    when = models.DateTimeField(_('firing time'), auto_now_add=True)

    msg = models.CharField(_('message'), max_length=1024)


class MessageLog(Message):
    class Meta:
        verbose_name = _(_('Message Log'))
        verbose_name_plural = _(_('Message Logs'))

    message = models.ForeignKey(Message)
  
    sms_log = models.TextField(_('SMS Log'), default='[]')
    gcm_log = models.TextField(_('GCM Log'), default='[]')
    apns_log = models.TextField(_('APNS Log'), default='[]')
    fail_log = models.TextField(_('Failed Message Log'), default='[]')


class DjangoInterface(FrameworkInterface):
    def add_message(sender, target, msg, when=datetime.now()):
        msg = Message()
        msg.sender = sender
        msg.target = target
        msg.when = when

        msg.msg = msg
        msg.save()

        if when <= datetime.now():
            return workers.worker()

        return None

    # must implemented to use sms type
    def get_sender_cell(sender_id):
        pass

    def query_messages():
        return Message.objects.filter(when <= datetime.now())

    def delete_messages(msg):
        msg.delete()

    def get_uri(msg_obj):
        return msg_obj.target

    def write_log(msg_obj, sms_log, gcm_log, apns_log, fail_log):
        log = MessageLog()

        log.message = msg_obj
        log.sms_log = sms_log
        log.gcm_log = gcm_log
        log.apns_log = apns_log
        log.fail_log = fail_log

        log.save()


MessageInterface.register(DjangoMessageInterface)
