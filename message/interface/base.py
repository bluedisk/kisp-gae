# -*- coding:utf-8 -*-

class FrameworkInterface:
    def add_messages(sender, target, title, msg, when=datetime.now()):
        raise NotImplementedError()

    def query_messages():
        raise NotImplementedError()

    def get_uri(msg_obj):
        raise NotImplementedError()

    def write_log(msg_obj, sms_log, gcm_log, apns_log, fail_log):
        pass

    def get_sender_cell(sender_id):
        pass
