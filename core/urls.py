# -*- coding:utf-8 -*-
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, FormView

from core.views import KISPPageView

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

urlpatterns = patterns('',
    url(r'^$', 'core.views.index',name='index'),
    url(r'^about/$', KISPPageView.as_view(), {'viewname':'about'}, name="about"),
    url(r'^aboutoz/$', KISPPageView.as_view(), {'viewname':'aboutoz'}, name="aboutoz"),
    url(r'^request/$', KISPPageView.as_view(), {'viewname':'request'}, name="request"),
    url(r'^team/$', KISPPageView.as_view(), {'viewname':'team_table'}, name="team"),
    
    url(r'^event/$', 'core.views.event_list', name='event_list'),
    url(r'^event/(?P<eid>\d+)/$', 'core.views.event', name='event'),

    url(r'^event/(?P<eid>\d+)/export/$', 'core.xlexport.agent', name='export_agent'),

    url(r'^event/image/add/(?P<eid>\d+)/$', 'core.views.event_image_add', name='event_image_add'),
    url(r'^event/image/del/(?P<eid>\d+)/(?P<iid>\d+)/$', 'core.views.event_image_del', name='event_image_del'),

    url(r'^entry/(?P<entry_id>\d+)/$', 'core.views.entry_view', name='entry_view'),
    url(r'^entry/(?P<event_id>\d+)/add/$', 'core.views.entry_edit', name='entry_add'),
    url(r'^entry/(?P<entry_id>\d+)/edit/$', 'core.views.entry_edit', name='entry_edit'),

    url(r'^entry/(?P<event_id>\d+)/agent/add/$', 'core.views.agent_entry_edit', name='agent_entry_add'),
    url(r'^entry/(?P<event_id>\d+)/agent/edit/$', 'core.views.agent_entry_edit', name='agent_entry_edit'),
    url(r'^entry/(?P<event_id>\d+)/agent/del/$', 'core.views.agent_entry_del', name='agent_entry_del'),
    
    url(r'^contact/$', 'core.views.contact', name='contact'),

    url(r'^sms/entry/$', 'core.views.send_sms_by_entry', name='send_sms_by_entry'),
    url(r'^sms/event/(?P<eid>\d+)/$', 'core.views.send_sms_by_event', name='send_sms_by_event'),

    url(r'^sms_sender/$', "core.views.sms_sender", name="sms_sender"),
  

    url(r'^signin/$', 'core.views.signin', name='signin'),
    url(r'^signout/$', 'core.views.signout', name='signout'),
    url(r'^signup/$', 'core.views.signup', name='signup'),
    url(r'^agent/$', 'core.views.agent_view', name='agent_view'),
    url(r'^agent/edit/$', 'core.views.agent_edit', name='agent_edit'),
    url(r'^passwd/$', 'core.views.change_pw', name='change_pw'),
    url(r'^reset/$', 'core.views.reset_pw', name='reset_pw'),

    url(r'^agent/image/(?P<agent_id>\d+)/$', 'core.views.agent_image', name='agent_image'),
)
