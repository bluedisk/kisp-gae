#!/usr/bin/env
# -*- coding:utf-8 -*-

from django.db import models
from djangotoolbox.fields import ListField, EmbeddedModelField
from core.fields import ModelListField
from tinymce.models import HTMLField

from django.template.defaultfilters import truncatechars  # or truncatewords
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from datetime import date, datetime, timedelta
from core import timezone

from gettext import gettext as _

import logging
logger = logging.getLogger('model')
logger.setLevel(logging.INFO)

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
		ordering = ['distance',]

	def __unicode__(self):
		return "%s (%s)"%(self.title,self.distance)

	title = models.CharField(u'코스명', max_length=255)
	distance = models.FloatField(u'거리')

EVENT_STATUS_INFO = {
	'ended':{
	'title':u'대회 종료',
	'description':u'모든 진행이 종료 되었습니다.',
	'class':'default'
	},
	'feedback':{
	'title':u'종료 보고 중',
	'description':u'대회가 종료 되었습니다. 종료 보고를 입력해주세요.',
	'class':'info'
	},
	'progress':{
	'title':u'대회 진행 중',
	'description':u'대회가 지금 현재 진행 중 입니다.',
	'class':'primary'
	},
	'organizing':{
	'title':u'모집 마감',
	'description':u'모집이 마감되었습니다.',
	'class':'danger'
	},
	'recruit_ending':{
	'title':u'모집 중',
	'description':u'곧 모집이 마감됩니다.',
	'class':'warning'
	},
	'recruit':{
	'title':u'모집 중',
	'description':u'모집을 진행중입니다.',
	'class':'success'
	},
	'ready_ending':{
	'title':u'모집 준비 중',
	'description':u'곧 모집을 시작합니다.',
	'class':'info'
	},
	'ready':{
	'title':u'모집 준비 중',
	'description':u'아직 모집 기간이 아닙니다.',
	'class':'default'
	},
	'none':{
	'title':u'',
	'description':u'',
	'class':'muted'
	}
}

class Event(models.Model):

	class Meta:
		verbose_name = u"행사"
		verbose_name_plural = u"행사들"
		ordering = ['-event_day']

	def __unicode__(self):
		return self.title

	def year_title(self):
		return '<code>'+self.event_day.strftime(u'%Y') + '</code> ' + self.short_title

	def course_list(self):
		return ", ".join( (course.title for course in Course.objects.filter(pk__in=self.course) ) )

	def entry_count(self):
		return Entry.objects.filter(event=self).count()

	def is_registable(self):

		today = timezone.today()

		if self.recruit_open > today:
			return False
		if self.recruit_deadline < today:
			return False

		return True

	def can_feedback(self):
		status = self.get_status()
		return status in ('progress','feedback','ended')

	def location_tag(self):
		if self.location_url:
			return '<a href="%s">%s</a>'%(self.location_url, self.location)

		return self.location

	def event_day_display(self):
		WEEKDAY_KOR = u"월화수목금토일-------"
		return u"%s년 %s월 %s일 (%s)"%(self.event_day.year, self.event_day.month, self.event_day.day, WEEKDAY_KOR[self.event_day.weekday()])

	def featured_image(self):
		try:
			return EventImage.objects.get(event=self, featured=True).image.url+'=s280-c'
		except:
			pass

		try:
			return EventImage.objects.filter(event=self, featured=False)[0].image.url+'=s280-c'
		except:
			pass

		return 'http://placehold.it/280x280&text=no+image'

	def get_status(self):

		today = timezone.today()
		tomorrow = today + timedelta(days=1)

		status = 'none';

		if self.feedback_deadline < today:
			status = 'ended'

		elif self.event_day < today and self.feedback_deadline >= today:
			status = 'feedback'

		elif self.event_day == today:
			status = 'progress'

		elif self.recruit_deadline < today:
			status = 'organizing'

		elif self.recruit_open <= today:
			status = 'recruit'

		elif self.recruit_open > today:
			status = 'ready'

		return status

	def get_status_info(self):

		today = timezone.today()

		tomorrow = today + timedelta(days=1)

		status = 'none';

		if self.feedback_deadline < today:
			status = 'ended'

		elif self.event_day < today and self.feedback_deadline >= today:
			status = 'feedback'

		elif self.event_day == today:
			status = 'progress'

		elif self.recruit_deadline < today:
			status = 'organizing'

		elif self.recruit_open <= today:
			if self.recruit_deadline == tomorrow:
				status = 'recruit_ending'

			elif self.recruit_deadline >= today:
				status = 'recruit'

		elif self.recruit_open == tomorrow:
			status = 'ready_ending'

		elif self.recruit_open > today:
			status = 'ready'

		return EVENT_STATUS_INFO[status]

	def get_status_text(self):
		return self.get_status_info()['title']

	def get_status_class(self):
		return self.get_status_info()['class']

	title = models.CharField(u'행사명',max_length=255)
	short_title = models.CharField(u'짧은 행사명',max_length=30)

	series = models.ForeignKey(u'Series', verbose_name=u'시리즈명', related_name=u'event')
	company = models.ForeignKey(EventCompany, verbose_name=u'이벤트사', related_name=u'event')

	desc = models.TextField(u'세부설명', blank=True)
	requested = models.IntegerField(u'요청 인원(명)', blank=True, default=20)

	location = models.CharField(u'장소', max_length=255)
	location_url = models.CharField(u'장소링크', max_length=255)

	support = models.IntegerField(u'지원금액', default=15000)

	course = ModelListField(Course,'title')
	participants = models.TextField(u'참가자 설명', blank=True)

	event_day = models.DateField(u'대회일', blank=True)
	assemble_time = models.TimeField(u'집결 시간', blank=True)
	race_time = models.TimeField(u'출발 시간', blank=True)

	recruit_open = models.DateField(u'등록 시작일', blank=True, null=True)
	recruit_deadline = models.DateField(u'등록 마감일', blank=True, null=True)
	feedback_deadline = models.DateField(u'후기 작성 종료일', blank=True, null=True)




class EventImage(models.Model):
	class Meta:
		verbose_name = u"행사 사진"
		verbose_name_plural = u"행사 사진들"
		ordering = ['event','order']

	def __unicode__(self):
		return self.title

	title = models.CharField(u'이미지설명', max_length=255, blank=True)
	image = models.FileField(upload_to=u'event/images/', verbose_name=u'이미지')
	featured = models.BooleanField(verbose_name=u'표지 사진 여부')
	event = models.ForeignKey(Event, verbose_name=u'행사', related_name='images')
	order = models.IntegerField('순서', default=0)

ENTRY_TYPE_CHOICES = (
		(u'wk',u'도보 패트롤'),
		(u'il',u'인라인 패트롤'),
		(u'cp',u'본부/현장스탭'),
	)

DISTANCE_TYPE_CHOICES = (
		(u'0',u'본부'),
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

	def save(self):

		try:
			group = ContactGroup.objects.get(name=u'최종(자동업데이트)')

			try:
				group.items.get(cell=self.cell)

			except ObjectDoesNotExist:
				nitem = ContactItem()
				nitem.group = group
				nitem.name = self.name
				nitem.cell = self.cell
				nitem.etc1 = u'자동추가 @%s' % self.event.title
				nitem.save()

		except ObjectDoesNotExist:
			logger.error('Auto Update ContactGroup Not Found')
		except:
			logger.error('Unknown Exception')
			pass

		super(Entry,self).save()


	def digest(self):
		digest = {
			'display':"%s (%sXXXX)"%(self.name,self.cell[:-4]),
			'name':self.name,
			'entry':self.pk
		}
		return digest

	def short_etc(self):
		return truncatechars(self.etc, 20)

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

	club = models.CharField(u'소속 동호회', max_length=128)

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
    callee = models.TextField(u'수신자')

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
	callee = models.TextField(u'수신자')

	msg = models.CharField(u'메시지',max_length=4096)

	timestamp = models.DateTimeField(u'예약시간')

class ContactGroup(models.Model):

    class Meta:
        verbose_name = _(u'연락처 그룹')
        verbose_name_plural = _(u'연락처 그룹들')

    def __unicode__(self):
        return u"[%s 그룹]" % self.name

    name = models.CharField(u'그룹명', max_length=255)


class ContactItem(models.Model):
    class Meta:
        verbose_name = _(u'연락처')
        verbose_name_plural = _(u'연락처들')

    def __unicode__(self):
        return self.name

    group = models.ForeignKey(ContactGroup, verbose_name=u'그룹', related_name='items')
    name = models.CharField(u'이름', max_length=255)
    cell = models.CharField(u'휴대폰', max_length=255)
    etc1 = models.CharField(u'기타1', max_length=255)
    etc2 = models.CharField(u'기타2', max_length=255)


class Feedback(models.Model):
	class Meta:
		verbose_name = _(u'패트롤 후기')
		verbose_name_plural = _(u'패트롤 후기들')

	def __unicode__(self):
		return "[%s] %s"%(self.event.short_title, self.name)

	def remain(self):
		return self.event.support - self.spend

	confirm = models.BooleanField(u'승인여부', default=False)
	event = models.ForeignKey(Event, verbose_name=u'행사')

	name = models.CharField(u'대원명', max_length=256)
	cell = models.CharField(u'휴대폰', max_length=30, blank=True)
	regnum = models.CharField(u'주민번호', max_length=15)


	where = models.CharField(u'사용 내역', max_length=256, blank=True)
	spend = models.IntegerField(u'사용 금액')

	patient = models.TextField(u'발생한 환자', blank=True)
	report = models.TextField(u'전달 할 사항', blank=True)
	suggest = models.TextField(u'제안 할 사항', blank=True)

class Point(models.Model):
    class Meta:
        verbose_name = _('Point')
        verbose_name_plural = _('Points')

    def __unicode__(self):
        return "%s - %s : %s"%(self.name, self.reason, self.amount)

    def when(self):
    	return self.created_at.strftime('%Y-%m-%d')

    name = models.CharField(u'이름', max_length=128)
    club = models.CharField(u'동호회', max_length=128, default=u'KISP')
    regnum = models.CharField(u'주민번호', max_length=15)

    reason = models.CharField(u'사유', max_length=1024)
    amount = models.IntegerField(u'금액')

    created_at = models.DateTimeField(u'등록일', auto_now_add=True)



