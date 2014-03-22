#!/usr/bin/env 
# -*- coding:utf-8 -*-

from django.db import models
from djangotoolbox.fields import ListField, EmbeddedModelField
from core.fields import ModelListField
from tinymce.models import HTMLField

from django.contrib.auth.models import User
from datetime import date, datetime
from gettext import gettext as _

class Series(models.Model):

	class Meta:
		verbose_name = u"시리즈 행사"
		verbose_name_plural = u"시리즈 행사 목록"

	def __unicode__(self):
		return self.title

	title = models.CharField(u'행사 시리즈 명',max_length=255)
	host = models.CharField(u'주최사', max_length=255)
	contact = models.TextField(u'연락처', blank=True)


class EventCompany(models.Model):

	class Meta:
		verbose_name = u"이벤트 업체"
		verbose_name_plural = u"이벤트 업체들"

	def __unicode__(self):
		return self.name

	name = models.CharField(u'업체명', max_length=255)
	desc = models.TextField(u'설명', blank=True)
	contact = models.TextField(u'연락처', blank=True)


class Course(models.Model):

	class Meta:
		verbose_name = u"# 코스 종류"
		verbose_name_plural = u"# 코스 종류 들"
		ordering = (u'distance',)

	def __unicode__(self):
		return "%s (%s)"%(self.title,self.distance)

	title = models.CharField(u'코스명', max_length=255)
	distance = models.FloatField(u'거리')
 

class Event(models.Model):
	
	class Meta:
		verbose_name = u"행사"
		verbose_name_plural = u"행사들"

	def __unicode__(self):
		return self.title

	def year_title(self):
		return '<code>'+self.event_day.strftime(u'%Y') + '</code> ' + self.short_title

	def course_list(self):
		return ", ".join( (course.title for course in Course.objects.filter(pk__in=self.course) ) )

	def entry_count(self):
		return Entry.objects.filter(event=self).count()

	def is_registable(self):
		today = date.today()
		if self.regist_start > today:
			return False
		if self.regist_end < today:
			return False

		return True

	def location_tag(self):
		if self.location_url:
			return '<a href="%s">%s</a>'%(self.location_url, self.location)

		return self.location

	
	def event_day_display(self):
		WEEKDAY_KOR = u"월화수목금토일-------"
		return u"%s년 %s월 %s일 (%s)"%(self.event_day.year, self.event_day.month, self.event_day.day, WEEKDAY_KOR[self.event_day.weekday()])

	title = models.CharField(u'행사명',max_length=255)
	short_title = models.CharField(u'짧은 행사명',max_length=30)

	desc = models.TextField(u'세부설명', blank=True)

	series = models.ForeignKey(u'Series', verbose_name=u'시리즈명', related_name=u'event')
	company = models.ForeignKey(EventCompany, verbose_name=u'이벤트사', related_name=u'event')

	course_map = models.ImageField(upload_to=u'map/',null=True, blank=True, verbose_name=u'코스지도')

	location = models.CharField(u'장소', max_length=255)
	location_url = models.CharField(u'장소링크', max_length=255)

	course = ModelListField(Course,'title')
	participants = models.TextField(u'참가자', blank=True)

	regist_start = models.DateField(u'등록 시작일', blank=True)
	regist_end = models.DateField(u'등록 마감일', blank=True)

	event_day = models.DateField(u'대회일', blank=True)
	assemble_time = models.TimeField(u'집결 시간', blank=True)
	race_time = models.TimeField(u'출발 시간', blank=True)

	requested = models.IntegerField(u'요청 인원(명)', blank=True, default=20)


class EventImage(models.Model):
	class Meta:
		verbose_name = u"행사 사진"
		verbose_name_plural = u"행사 사진들"

	def __unicode__(self):
		return self.title

	image = models.FileField(upload_to=u'event_image/', verbose_name=u'이미지들')
	title = models.CharField('이미지설명', max_length=255)
	event = models.ForeignKey(Event, verbose_name=u'행사', related_name='images')

ENTRY_TYPE_CHOICES = (
		(u'wk',u'도보 패트롤'),
		(u'il',u'인라인 패트롤'),
		(u'cp',u'본부/현장스탭'),
	)

DISTANCE_TYPE_CHOICES = (
		(u'5',u'0~5Km'),
		(u'10',u'5~10Km'),
		(u'20',u'10~20Km'),
		(u'30',u'20~30Km'),
		(u'30+',u'30Km 이상'),
	)

TSIZE_CHOICES = (
		(u'85',u'85(XS)'),
		(u'90',u'90(S)'),
		(u'95',u'95(M)'),
		(u'100',u'100(L)'),
		(u'105',u'105(XL)'),
		(u'110',u'110(XXL)'),
	)

CARPOOL_TYPE_CHOICES = (
		(u'none', u'카풀 안함(기본)'),
		(u'serv', u'카풀 제공 가능'),
		(u'need', u'카풀 받기를 원함'),
	)

class Skill(models.Model):
    class Meta:
        verbose_name = _('# Skill')
        verbose_name_plural = _('# Skills')

    def __unicode__(self):
        return self.name

    name = models.CharField(u'스킬명', max_length=32)
    desc = models.TextField(u'부가설명', blank=True)
    

class Entry(models.Model):

	class Meta:
		verbose_name = u"패트롤 신청"
		verbose_name_plural = u"패트롤 신청 목록"

	def __unicode__(self):
		return self.name

	def digest(self):
		digest = {
			'display':"%s (%sXXXX)"%(self.name,self.cell[:-4]),
			'entry':self.pk
		}
		return digest
	
	def carpool_digest(self):
		digest = {
			'display': "%s (%s)"%(self.name,self.location),
			'entry': self.pk
		}
		return digest

	def skill_display(self):
		skill = [ sk.name for sk in Skill.objects.filter(pk__in=self.skill)]
		return ", ".join(skill)

	skill_display.short_description = u"가능 기술"

	event = models.ForeignKey(Event, verbose_name=u'행사')
	user = models.ForeignKey(User, verbose_name=u'대원', null=True, blank=True)

	name = models.CharField(u'이름', max_length=32)
	cell = models.CharField(u'휴대폰', max_length=32)
	regnum = models.CharField(u'주민번호', max_length=15)

	htype = models.CharField(u'희망타입', max_length=2, choices=ENTRY_TYPE_CHOICES, blank=True)
	hdist = models.CharField(u'희망거리', max_length=5, choices=DISTANCE_TYPE_CHOICES, blank=True)

	carpool = models.CharField(u'카풀여부', max_length=4, choices=CARPOOL_TYPE_CHOICES, blank=True)
	location = models.CharField(u'지역', max_length=32, blank=True)

	tsize = models.CharField(u'티셔츠사이즈', max_length=5, choices=TSIZE_CHOICES)
	mileage = models.CharField(u'마일리지', max_length=32, blank=True)

	skill = ModelListField(Skill,'name')

	etc = models.TextField(u'요청사항', blank=True)


class Agent(models.Model):

	class Meta:
		verbose_name = u"대원"
		verbose_name_plural = u"대원 명단"

	def __unicode__(self):
		return "%s(%s)"%(self.user.first_name, self.user.username)

	def regnum_masked(self):
		return self.regnum[:6]+"-*******"
	
	def skill_display(self):
		skill = [ sk.name for sk in Skill.objects.filter(pk__in=self.skill)]
		return ", ".join(skill)

	def image_url(self):
		if self.image.name:
			return self.image.url+'=s280-c'

		return '/static/image/noface.png'

	user = models.OneToOneField(User, related_name='agent')

	cell = models.CharField(u'휴대폰', max_length=32)
	regnum = models.CharField(u'주민번호', max_length=15)
	mileage = models.CharField(u'마일리지', max_length=32, blank=True)
	tsize = models.CharField(u'티셔츠사이즈', max_length=5, choices=TSIZE_CHOICES, blank=True)

	image = models.FileField(upload_to=u'agent_image/', null=True, blank=True, verbose_name=u'대원사진(140x140 권장)')

	skill = ModelListField(Skill,'name')

	location = models.CharField(u'지역', max_length=32, blank=True)

	# def save(self, size=(140, 140)): 
	# 	super(Agent, self).save() 
	# 	if self.image: 
	# 		image = Image.open(self.image) 

	# 		image.thumbnail(size, Image.ANTIALIAS) 
	# 		self.image = image

class Page(models.Model):

	class Meta:
		verbose_name = u"페이지"
		verbose_name_plural = u"페이지 목록"

	def __unicode__(self):
		return self.title

	name = models.CharField(u'페이지명', max_length=32, primary_key=True)
	title = models.CharField(u'제목',max_length=256, blank=True)
	subtitle = models.CharField(u'부제목',max_length=1024, blank=True)
	content = HTMLField(u'')

class SMSLog(models.Model):
    
    class Meta:
        verbose_name = u"SMS 전송 로그"
        verbose_name_plural = u"SMS 전송 로그"
 
    def __unicode__(self):
        return u"[%s] 폰번호 %s 에서 %d개 발송"%(self.timestamp.isoformat(), self.caller, self.count)
    
    caller = models.CharField(u'발신자', max_length=30)
    callee = models.CharField(u'수신자', max_length=4096)

    msg = models.CharField(u'메시지',max_length=4096)

    #user = models.ForeignKey(User, verbose_name=u'발송자', blank=True)
    count = models.IntegerField(u'발송된 갯수')
    
    timestamp = models.DateTimeField(u'전송시간', auto_now_add=True, blank=True)


class ReservedSMS(models.Model):

	class Meta:
		verbose_name = u"SMS 예약"
		verbose_name_plural = u"SMS 예약"

	def __unicode__(self):
		target = self.callee.split(",");

		if len(target) == 1:
			target = target[0]
		else:
			target = u"%s외 (%s명)"%(target[0],len(target)-1)
		
		return u"[%s] %s=>%s"%(self.timestamp.isoformat(), self.caller, target )

	caller = models.CharField(u'발신자', max_length=30)
	callee = models.CharField(u'수신자', max_length=4096)

	msg = models.CharField(u'메시지',max_length=4096)

	timestamp = models.DateTimeField(u'예약시간')

class ContactGroup(models.Model):
    class Meta:
        verbose_name = _('ContactGroup')
        verbose_name_plural = _('ContactGroups')

    def __unicode__(self):
        return self.name

    name = models.CharField(u'그룹명', max_length=255)

    
class ContactItem(models.Model):
    class Meta:
        verbose_name = _('ContactItem')
        verbose_name_plural = _('ContactItems')

    def __unicode__(self):
        return self.name
    
    group = models.ForeignKey(ContactGroup, verbose_name=u'그룹')
    name = models.CharField(u'이름', max_length=255)
    cell = models.CharField(u'휴대폰', max_length=255)
    etc1 = models.CharField(u'기타1', max_length=255)
    etc2 = models.CharField(u'기타1=2', max_length=255)
