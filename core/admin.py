# -*- coding:utf-8 -*-
from django.contrib import admin
from django.core.urlresolvers import reverse

from django.forms import ModelForm
from django.http import HttpResponseRedirect

from core.models import Event, EventImage, EventCompany, Series, Course, Entry, Agent, Page, SMSLog, ReservedSMS, Skill
from core.models import ContactGroup, ContactItem, Feedback

from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class EventImageAdmin(admin.ModelAdmin):
    list_filter=('event',)
    list_display=('event','title','order',)
    ordering=('event','order',)

    list_editable=('title','order',)

class EventAdmin(admin.ModelAdmin):
    class Media:
        from django.conf import settings
        js = [ '/static/js/admin-date-autoset.js', ]

    list_display = ('title','location','event_day')

    fieldsets = (
        (u'행사 제목', {
            'fields':('title','short_title','series','company'),
            }),
        (u'행사 정보', {
            'fields':(("location",'location_url'),'support','course','requested','desc','participants'),
            }),        
        (u'행사 일정', {
            'fields':('event_day','assemble_time','race_time'),
            }),
        (u'진행 일정', {
            'fields':('recruit_open','recruit_deadline','feedback_deadline'),
            }),
    )

    # def send_sms(self, request, queryset):
    #     selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    #     return HttpResponseRedirect(reverse('send_sms_by_event')+"id=%s"%(",".join(selected)))

    # send_sms.short_description = u"[SMS] 선택된 행사 참가 대원들에게 문자 메시지를 전송합니다."

    # actions = [send_sms]
    

class EventCompanyAdmin(admin.ModelAdmin):
    pass

class SeriesAdmin(admin.ModelAdmin):
    pass

class CourseAdmin(admin.ModelAdmin):
    pass

class EntryAdmin(admin.ModelAdmin):
    list_display=('name','cell','mileage','htype','hdist','skill_display','short_etc')
    list_filter=('event','htype')

    # fieldset = (
    #     ('Title', {
    #         'fields':('title',"subtitle"),
    #         }),
    #     ('detail', {
    #         'classes':('wide',),
    #         'fields': ('subtitle', 'content')
    #         }   
    #     )
    # )

    # def send_sms(self, request, queryset):
    #     selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
    #     return HttpResponseRedirect(reverse('send_sms_by_entry')+"ids=%s"%(",".join(selected)))

    # send_sms.short_description = u"[SMS] 선택된 대원에게 문자 메시지를 전송합니다."

    # actions = [send_sms]

class AgentAdmin(admin.ModelAdmin):
    list_display=('user','cell','mileage',)


class PageAdmin(admin.ModelAdmin):
    pass

class SMSLogAdmin(admin.ModelAdmin):
    list_display=('timestamp', 'caller','callee','count')



admin.site.register(Event, EventAdmin)
admin.site.register(EventImage, EventImageAdmin)
admin.site.register(EventCompany, EventCompanyAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Course, CourseAdmin)

admin.site.register(Entry, EntryAdmin)
admin.site.register(Agent, AgentAdmin)
admin.site.register(Page, PageAdmin)

admin.site.register(SMSLog, SMSLogAdmin)
admin.site.register(ReservedSMS)
admin.site.register(Skill)

admin.site.register(ContactGroup)
admin.site.register(ContactItem)
admin.site.register(Feedback)