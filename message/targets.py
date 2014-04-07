# -*- coding:utf-8 -*-
from urlparse import urlparse
from message.utils import format_cell


def dummy_parser(model, id, field):
    return None

class Target:
    uri_text = None
    uri = None

    def __init__(text=None):
        uri_text=text
        uri = urlparse(uri_text)
    
    def __unicode__(self):
        return uri_text

    @property
    def type(self):
        return self.uri.scheme

    @property
    def id(self):
        return self.uri.username

    @property
    def model(self):
        return self.uri.netloc
  

class TargetParser:

    uri_parsers = {}
 
    @staticmethod
    def get_parser(model):
        if model in TargetParser.uri_parsers:
            return TargetParser.uri_parsers[model]

        return None

    @staticmethod
    def register_parser(classname, parser):
        TargetParser.uri_parsers[classname] = parser

    @staticmethod
    def unregister_parser(classname):
        if classname in TargetParser.uri_parsers:
            TargetParser.uri_parsers[classname]=None



class TargetFactory:

    @staticmethod
    def from_uri(uri):
        uri = urlparse(uris)

        if uri.scheme != u"model":
            return Target(uri)

        parser = MessageParser.get_parser(uri.netloc) or dummy_parser
        if not parser:
            raise NotImplementedError('Parser for model %s not found!'%uri.netloc)

        return parser(model=uri.netloc, id=uri.username, field=uri.path)

    @staticmethod
    def from_cell(cell):
        cell = format_cell(cell)
        return Target(u'sms://%s/'%cell)

    @staticmethod
    def from_token(push_model, token):
        return Target(u'push://%s@%s/'%(token,push_model))

    @staticmethod
    def from_model(model, id, field):
        return Target(u'model://%s@%s/%s/'%(id, model, field))

