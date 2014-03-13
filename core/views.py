# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView
from django.forms.util import ErrorDict
from django.http import HttpResponseRedirect, HttpResponse

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from core.models import Event, Entry, Agent, Page, ReservedSMS
from core.forms import EntryForm, AgentEntryForm, SendSmsForm, UserSignupForm, UserSigninForm, AgentForm
from core.sms import sendSMS

from datetime import datetime, date, timedelta
import logging

def index(request):
	return render(request,'core/index.html', {'events':Event.objects.all()})

def event_list(request):
	events = Event.objects.all();
	return render(request,'core/event_list.html', {'viewname':'event-list', 'events':events})

def event(request,eid):
	event = Event.objects.get(pk=eid)

	all_entries = Entry.objects.filter(event__pk=eid)
	entries = [entry.digest() for entry in all_entries]
	carpools = {
		'servers': [entry.carpool_digest() for entry in all_entries.filter(carpool='serv')],
		'needs': [entry.carpool_digest() for entry in all_entries.filter(carpool='need')]
	}

	entry = None
	if request.user.is_authenticated():
		try:
			entry = Entry.objects.get(event= event, user = request.user)
		except:
			pass

	today = date.today()
	if event.regist_end < today:
		regist_hint = u'모집이 마감되었습니다.'
		regist_hint_class = 'text-danger'

	elif event.regist_end <= today+timedelta(days=1):
		regist_hint = u'곧 모집이 마감됩니다!'
		regist_hint_class = 'text-warning'

	elif event.regist_start == today+timedelta(days=1):
		regist_hint = u'곧 모집을 시작합니다.'
		regist_hint_class = 'text-success'
	elif event.regist_start > today:
		regist_hint = u'아직 모집 기간이 아닙니다.'
		regist_hint_class = 'text-success'
	else:
		regist_hint = u''
		regist_hint_class = ''



	return render(request,'core/event.html', {
		'viewname':'event-list', 
		'event':event ,
		'entries':entries, 
		'carpools':carpools,
		'entry':entry,
		'regist_hint': regist_hint,
		'regist_hint_class': regist_hint_class
	})

def entry_view(request,entry_id):
	me = False
	form = None
	entry = Entry.objects.get(pk=entry_id)

	if request.session.get('entry') == int(entry_id):
		me = True

	if request.method == 'POST':
		form = SendSmsForm(request.POST)
		last_sms = request.session.get('last_sms')

		if last_sms and (datetime.now() - last_sms) < timedelta(minutes=5):
			form._errors = ErrorDict()
			form._errors['msg'] = form.error_class()
			form._errors['msg'].append(u'너무 빈번한 요청 입니다. 5분을 기다려주세요.')

		if form.is_valid(): 
			request.session['last_sms'] = datetime.now()

			caller = form.cleaned_data['caller']
			callee = entry.cell
			msg = form.cleaned_data['msg']

			sendSMS(msg, caller, callee)

			return render(request,'core/sms_sent.html', {'entry':entry, 'sms':{'caller':caller, 'callee':callee, 'msg':msg }})
	else:
		form = SendSmsForm() # An unbound form


	return render(request,'core/entry_view.html', {
		'viewname':'event-list', 
		'my_entry_id':request.session.get('entry'),
		'entry':entry,
		'me':me,
		'form':form
	})

def entry_edit(request,entry_id=None, event_id=None):
	if entry_id and int(entry_id) != request.session.get('entry'):
		raise PermissionDenied()

	if entry_id:
		entry = Entry.objects.get(pk=entry_id)
	else:
		entry = None

	if event_id:
		event = Event.objects.get(pk=event_id)
	else:
		event = entry.event


	if request.method == 'POST':
		form = EntryForm(request.POST, instance=entry)

		if form.is_valid(): 
			entry = form.save(commit=False)
			entry.event = event
			entry.save();

			request.session['entry'] = entry.pk

			return HttpResponseRedirect(reverse('entry_view', args=[entry.pk]))
	else:
		form = EntryForm(instance=entry) # An unbound form


	return render(request,'core/entry_edit.html', {
		'viewname':'event-list', 
		'entry':entry,
		'event':event,
		'form':form, 

	})

@login_required
def agent_entry_edit(request, event_id=None):

	user = request.user
	event = Event.objects.get(pk=event_id)

	try:
		entry = Entry.objects.get(event=event, user=user)
		initial= None
	except:
		entry = None
		initial= {
			'name': user.first_name,
			'cell': user.agent.cell,
			'regnum' : user.agent.regnum,
			'tsize': user.agent.tsize,
			'mileage': user.agent.mileage,
			'location': user.agent.location,
			'skill': user.agent.skill
		}

	if request.method == 'POST':
		form = AgentEntryForm(request.POST,instance=entry)

		if form.is_valid(): 
			entry = form.save(commit=False)
			entry.event = event
			entry.user = user
			entry.save();

			request.session['entry'] = entry.pk

			return HttpResponseRedirect(reverse('entry_view', args=[entry.pk]))
	else:
		form = AgentEntryForm(instance=entry, initial=initial) # An unbound form


	return render(request,'core/entry_edit.html', {
		'viewname':'event-list', 
		'event':event,
		'form':form, 
	})

def contact(request):

	def extract_user(agent):
		name = agent.user.first_name
		image = '/static/image/noface.png'

		if agent.image.name:
			image = image.url

		return {'name':name, 'image':image }

	members = [ extract_user(agent) for agent in Agent.objects.all() ]
	padding = 5 - len(members) % 5

	if padding:
		for i in range(padding):
			members.append({'name':'', 'image':''})

   	return render(request, 'core/contact.html', {'viewname':'contact', 'members':members})


def send_sms_by_entry(request):
	entries = Entry.objects.filter(pk__in = request._GET['ids'].split(',') )
	return render(request, 'core/sms.html', {'viewname':'event', 'entries':entries})


def send_sms_by_event(request, eid):
	entries = Entry.objects.filter(event__pk=eid)
	return render(request, 'core/sms.html', {'viewname':'event', 'entries':entries})

class KISPPageView(DetailView):
	template_name = "core/kisppage.html"

	model = Page
	context_object_name = 'page'
	pk_url_kwarg = 'viewname'

	# def get_context_data(self, **kwargs):
	# 	context = super(KISPPageView, self).get_context_data(**kwargs)
	# 	page = get_object_or_404(Page, pk=kwargs['viewname'])
		
	# 	context['page'] = {
	# 		'title':page.title,
	# 		'subtitle':page.subtitle,
	# 		'content':page.content
	# 	}

	# 	return context

#logger = logging.getLogger('sms')
#logger.setLevel(logging.DEBUG)

def sms_sender(request):
	check_point = datetime.now() + timedelta(hours=9)
	
	sms = ReservedSMS.objects.filter(timestamp__lt = check_point)

	for item in sms:
		sendSMS( item.msg, item.caller, item.callee)
		
	ReservedSMS.objects.filter(timestamp__lt = check_point).delete()

	return HttpResponse("%s"%check_point)

def signup(request):

    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():

            new_user = form.save()
            new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])

            login(request, new_user)
            return HttpResponseRedirect(reverse('agent'))
    else:
        form = UserSignupForm()

    return render(request, "user/signup.html", { 'form': form, })

def signin(request):

	next = request.GET.get('next','/')

	if request.method == 'POST':
		form = UserSigninForm(request.POST)
		if form.is_valid():

			user = form.get_user()
			login(request, form.get_user())

			next = request.POST['next']
			if not Agent.objects.filter(user=user).count():
				next = reverse('agent')

			return HttpResponseRedirect(next)	
	else:
		form = UserSigninForm()

	return render(request, "user/login.html", { 'form': form, 'next':next })

@login_required
def signout(request):
	logout(request);
	return HttpResponseRedirect('/')

def reset_pw(request):

	

	return HttpResponse(request,"미안.. 아직 안만들었어..")

@login_required
def change_pw(request):

	if request.method == 'POST':
		form = UserChangePasswordForm(request.POST)
		if form.is_valid():

			user.set_password(form.cleaned_data['password'])
			user.save()

			return render(request, "user/change_pw_done.html")
	else:
		form = UserChangePasswordForm()

	return render(request, "user/change_pw_form.html", { 'form': form })

@login_required
def agent(request):
	
	saved=False

	try:	
		agent = request.user.agent
	except:
		agent = None

	if request.method == 'POST':
		form = AgentForm(request.POST)

		if form.is_valid():
			new_agent = form.save(commit=False)
			
			if agent:
				new_agent.pk = agent.pk

			new_agent.user = request.user
	
			new_agent.save()

			form = AgentForm(instance=new_agent)
			saved=True
#			return HttpResponseRedirect(reverse('/'))
	else:
		# try:
		# 	agent = Agent.objects.get(pk=request.user)
		# except:
		# 	agent = None
		
		form = AgentForm(instance=agent)

	return render(request, "user/agent.html", { 'form': form, 'saved':saved})




