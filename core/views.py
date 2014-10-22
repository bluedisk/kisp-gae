# -*- coding:utf-8 -*-
from django.shortcuts import render, render_to_response
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.views.generic import DetailView
from django.views.decorators.csrf import csrf_exempt

from django.forms.util import ErrorDict
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import redirect_to_login

from django.shortcuts import get_object_or_404

from core.models import Event, EventImage, Entry, Agent, Page, ReservedSMS, Feedback, Point
from core.models import ContactGroup, ContactItem
from core.forms import EntryForm, AgentEntryForm, SendSmsForm, SendUserSmsForm, UserSignupForm, UserSigninForm, UserChangePasswordForm, AgentForm, EventImageForm, FeedbackForm
from core.sms import sendSMS

from datetime import datetime, date, timedelta
import logging
import json

from filetransfers.api import serve_file, prepare_upload


def index(request):
    return render(request, 'core/index.html', {'events': Event.objects.all()[:6]})


def event_list(request):
    events = Event.objects.all()
    return render(request, 'core/event_list.html', {'viewname': 'event-list', 'events': events})


def event(request, eid):
    event = get_object_or_404(Event, id=eid)

    all_entries = Entry.objects.filter(event__pk=eid)
    entries = [entry.digest() for entry in all_entries]
    carpools = {
        'servers': [entry.carpool_digest() for entry in all_entries.filter(carpool='serv')],
        'needs': [entry.carpool_digest() for entry in all_entries.filter(carpool='need')]
    }

    entry = None
    if request.user.is_authenticated():
        try:
            entry = Entry.objects.get(event=event, user=request.user)
        except:
            pass

    status = event.get_status_info()

    status_text = status['description']
    status_class = 'text-' + status['class']

    try:
        featured = EventImage.objects.get(event=event, featured=True)
    except:
        featured = None

    images = EventImage.objects.filter(event=event, featured=False).order_by('order')

    feedbacks = list(f.name for f in Feedback.objects.filter(event=event, confirm=False))
    confirmed = list(f.name for f in Feedback.objects.filter(event=event, confirm=True))

    return render(request, 'core/event.html', {
        'viewname': 'event-list',
        'event': event,
        'featured': featured,
        'images': images,
        'entries': entries,
        'feedbacks': feedbacks,
        'confirmed': confirmed,
        'carpools': carpools,
        'entry': entry,
        'status_text': status_text,
        'status_class': status_class
    })


def entry_view(request, entry_id):
    me = False
    form = None
    entry = get_object_or_404(Entry, pk=entry_id)

    if request.session.get('entry') == int(entry_id):
        me = True

    if request.user.is_authenticated() and request.user == entry.user:
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

            return render(request, 'core/carpool_sms_sent.html', {'entry': entry, 'sms': {'caller': caller, 'callee': callee, 'msg': msg}})
    else:
        # An unbound form
        form = SendSmsForm()

    return render(request, 'core/entry_view.html', {
        'viewname': 'event-list',
        'my_entry_id': request.session.get('entry'),
        'entry': entry,
        'me': me,
        'form': form
    })


def entry_preadd(request, event_id=None):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('agent_entry_add', args=[event_id, ]))

    if request.method == 'POST':
        return HttpResponseRedirect(reverse('entry_add', args=[event_id, request.POST['club']]))

    return render(request, 'core/club_search.html', {'event': event_id, 'club': ''})


def entry_edit(request, entry_id=None, event_id=None, club=u''):
    if entry_id and int(entry_id) != request.session.get('entry'):
        raise PermissionDenied()

    if entry_id:
        entry = get_object_or_404(Entry, pk=entry_id)
    else:
        entry = None

    if event_id:
        event = get_object_or_404(Event, pk=event_id)
    else:
        event = entry.event

    if request.method == 'POST':
        form = EntryForm(request.POST, instance=entry)

        if form.is_valid():
            entry = form.save(commit=False)
            entry.event = event
            entry.save()

            request.session['entry'] = entry.pk

            return HttpResponseRedirect(reverse('entry_view', args=[entry.pk]))
    else:
        # An unbound form
        form = EntryForm(instance=entry, initial={'club': club})

    return render(request, 'core/entry_edit.html', {
        'viewname': 'event-list',
        'entry': entry,
        'event': event,
        'form': form,
    })


@login_required
def agent_entry_edit(request, event_id=None):

    user = request.user
    agent = None
    try:
        agent = user.agent
    except:
        return HttpResponseRedirect(reverse('agent_edit'))

    event = get_object_or_404(Event, pk=event_id)

    try:
        entry = Entry.objects.get(event=event, user=user)
        initial = None
    except:
        entry = None
        initial = {
            'name': user.first_name,
            'cell': user.agent.cell,
            'regnum': user.agent.regnum,
            'club': u'KISP',
            'tsize': user.agent.tsize,
            'mileage': user.agent.mileage,
            'location': user.agent.location,
            'skill': user.agent.skill
        }

    if request.method == 'POST':
        form = AgentEntryForm(request.POST, instance=entry)

        if form.is_valid():
            entry = form.save(commit=False)
            entry.event = event
            entry.user = user
            entry.save()

            request.session['entry'] = entry.pk

            return HttpResponseRedirect(reverse('entry_view', args=[entry.pk]))
    else:
        # An unbound form
        form = AgentEntryForm(instance=entry, initial=initial)

    return render(request, 'core/entry_edit.html', {
        'viewname': 'event-list',
        'event': event,
        'form': form,
    })


@login_required
def agent_entry_del(request, event_id=None):
    return render(request, 'core/info.html', {
        'title': '공사중!',
        'msg': '죄송합니다. 이 기능은 아직 제작 중 입니다. 삭제를 원하시면 스탭에게 요청해주세요.',
    })


def contact(request):

    def extract_user(agent):
        name = agent.user.first_name
        image = agent.image_url

        return {'name': name, 'image': image}

    members = [extract_user(agent) for agent in Agent.objects.all()]
    padding = 5 - len(members) % 5

    if padding:
        for i in range(padding):
            members.append({'name': '', 'image': ''})

    return render(request, 'core/contact.html', {'viewname': 'contact', 'members': members})


@staff_member_required
def groups(request):
    return render(request, 'core/groups.html', {
        'groups': ContactGroup.objects.all(),
        'events': Event.objects.all()
    })


@staff_member_required
def send_sms_by_entry(request):
    entries = Entry.objects.filter(pk__in=request._GET['ids'].split(','))
    return send_sms(request, entries)


@staff_member_required
def send_sms_by_event(request, eid):
    event = Event.objects.get(pk=eid)
    entries = Entry.objects.filter(event__pk=eid)
    return send_sms(request, entries, str(event))


@staff_member_required
def send_sms_by_group(request, gid):
    group = ContactGroup.objects.get(pk=gid)
    entries = ContactItem.objects.filter(group__pk=gid)
    return send_sms(request, entries, str(group))


@staff_member_required
def send_sms(request, entries, title):
    form = None
    sent = False

    if request.method == 'POST':
        form = SendUserSmsForm(request.POST)

        if form.is_valid():
            callees = ",".join(entry.cell for entry in entries)
            sendSMS(form.cleaned_data['msg'], form.cleaned_data['caller'], callees)

            sent = True
            form = None

    if not form:
        caller = ''
        if request.user.agent:
            caller = request.user.agent.cell

        form = SendUserSmsForm(initial={'caller': caller, 'msg': '[KISP] '})

    return render(request, 'core/sms.html', {'viewname': 'event', 'title': title, 'entries': entries, 'form': form, 'sent': sent})


class KISPPageView(DetailView):
    template_name = "core/kisppage.html"

    model = Page
    context_object_name = 'page'
    pk_url_kwarg = 'viewname'

    # def get_context_data(self, **kwargs):
    #     context=super(KISPPageView, self).get_context_data(**kwargs)
    #     page=get_object_or_404(Page, pk=kwargs['viewname'])

    #     context['page']={
    #         'title':page.title,
    #         'subtitle':page.subtitle,
    #         'content':page.content
    #     }

    #     return context

#logger=logging.getLogger('sms')
#logger.setLevel(logging.DEBUG)


def sms_sender(request):
    check_point = datetime.now() + timedelta(hours=9)

    sms = ReservedSMS.objects.filter(timestamp__lt=check_point)

    for item in sms:
        sendSMS(item.msg, item.caller, item.callee)

    ReservedSMS.objects.filter(timestamp__lt=check_point).delete()

    return HttpResponse("%s" % check_point)


def signup(request):

    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():

            new_user = form.save()
            new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])

            if new_user is not None:
                if new_user.is_active:
                    login(request, new_user)
                    return HttpResponseRedirect(reverse('agent_edit'))

            return redirect_to_login(reverse('agent_edit'))
    else:
        form = UserSignupForm()

    return render(request, "user/signup.html", {'form': form, })


def signin(request):

    next = request.GET.get('next', '/')

    if request.method == 'POST':
        form = UserSigninForm(request.POST)
        if form.is_valid():

            user = form.get_user()
            login(request, form.get_user())

            next = request.POST['next']
            if not Agent.objects.filter(user=user).count():
                next = reverse('agent_edit')

            return HttpResponseRedirect(next)
    else:
        form = UserSigninForm()

    return render(request, "user/login.html", {'form': form, 'next': next})


@login_required
def signout(request):
    logout(request)
    return HttpResponseRedirect('/')


def reset_pw(request):

    return HttpResponse(request, "미안.. 아직 안만들었어..")


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

    return render(request, "user/change_pw_form.html", {'form': form})


@login_required
def agent_view(request):
    try:
        agent = request.user.agent
    except:
        agent = {
            'cell': u'등록안됨',
            'regnum_masked': u'등록안됨',
            'mileage': u'등록안됨',
            'tsize': u'등록안됨',
            'skill_display': u'등록안됨',
            'location': u'등록안됨',
            'image_url': u'/static/image/noface.png'
        }
    return render(request, "user/agent.html", {'agent': agent})


@login_required
def agent_edit(request):
    view_url = reverse('core.views.agent_edit')

    try:
        agent = request.user.agent
    except:
        agent = None

    if request.method == 'POST':
        form = AgentForm(request.POST, request.FILES)

        if form.is_valid():
            new_agent = form.save(commit=False)

            if agent:
                new_agent.pk = agent.pk

            new_agent.user = request.user

            if not new_agent.image and not request.POST.get('image-clear', False) and agent:
                new_agent.image = agent.image

            new_agent.save()

            #form=AgentForm(instance=new_agent)
            return HttpResponseRedirect(reverse('agent_view'))
    else:
        form = AgentForm(instance=agent)

    upload_url, upload_data = prepare_upload(request, view_url)

    return render(request, "user/agent_edit.html", {'form': form, 'upload_url': upload_url, 'upload_data': upload_data})


def agent_image(request, agent_id):
    agent = get_object_or_404(Agent, pk=agent_id)
    return serve_file(request, agent.file)


@login_required
def event_image_add(request, eid):
    view_url = reverse('core.views.event_image_add', args=[eid])
    event = get_object_or_404(Event, id=eid)

    if request.method == 'POST':
        form = EventImageForm(request.POST, request.FILES)

        if form.is_valid():

            if form.cleaned_data['featured']:
                EventImage.objects.filter(event=event, featured=True).update(featured=False)

            new_image = form.save(commit=False)
            new_image.event = event
            new_image.save()

            return HttpResponseRedirect(reverse('event', args=[eid]))
    else:
        form = EventImageForm()

    upload_url, upload_data = prepare_upload(request, view_url)
    return render(request, "core/event_image.html", {'form': form, 'event': event, 'upload_url': upload_url, 'upload_data': upload_data})


@login_required
def event_image_del(request, eid, iid):
    if request.user.is_staff:
        image = get_object_or_404(EventImage, pk=iid)
        image.delete()

    return HttpResponseRedirect(reverse('event', args=[eid]))


def feedback_write(request, eid):
    event = get_object_or_404(Event, id=eid)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('event', args=[eid]))
    else:
        if request.user.is_authenticated():

            try:
                agent = Agent.objects.get(user=request.user)
                cell = agent.cell
            except:
                cell = None

            regnum = ''
            if request.user.agent:
                regnum = request.user.agent.regnum

            form = FeedbackForm(initial={
                'uid': request.user.pk,
            })
        else:
            form = FeedbackForm()

    return render(request, "core/feedback_write.html", {'form': form, 'event': event})


@staff_member_required
@csrf_exempt
def feedback_update(request):

    if not request.method == 'POST':
        return HttpResponseBadRequest('need post request')

    if not all(x in ['fid', 'where', 'spend', 'patient', 'report', 'suggest'] for x in request.POST):
        return HttpResponseBadRequest('wrong argument')

    feedback = get_object_or_404(Feedback, id=request.POST['fid'])
    feedback.spend = request.POST['spend']
    feedback.where = request.POST['where']
    feedback.patient = request.POST['patient']
    feedback.report = request.POST['report']
    feedback.suggest = request.POST['suggest']
    feedback.save()

    return HttpResponse('ok')


@staff_member_required
def feedback(request, eid):
    event = get_object_or_404(Event, id=eid)
    feedbacks = Feedback.objects.filter(event=event)

    en_cnt = Entry.objects.filter(event=eid).count()
    fb_cnt = feedbacks.count()

    spend_sum = 0
    for fb in feedbacks:
        spend_sum = spend_sum + fb.spend

    saved_sum = fb_cnt * event.support - spend_sum

    return render(request, "core/feedback.html", {
        'feedbacks': feedbacks,
        'event': event,

        'entry_cnt': en_cnt,
        'feedback_cnt': fb_cnt,
        'spend': spend_sum,
        'saved': saved_sum,
    })


@staff_member_required
def feedback_confirm(request):
    event = Event.objects.get(id=request.POST['eid'])

    ids = request.POST['ids']
    ids = json.loads(ids)

    feedbacks = Feedback.objects.filter(id__in=ids)

    for feedback in feedbacks:
        feedback.confirm = True
        feedback.save()

        point = Point()
        point.name = feedback.name
        point.regnum = feedback.regnum
        point.reason = u"[정산] '%s' 적립금" % event.short_title
        point.amount = event.support - feedback.spend

        point.save()

    return HttpResponse('%s feedback(s) confirmed' % len(ids))


@staff_member_required
def feedback_delete(request):
    ids = request.POST['ids']
    ids = json.loads(ids)

    Feedback.objects.filter(id__in=ids).delete()

    return HttpResponse('%s feedback(s) deleted' % len(ids))


def event_reserved_sms(request, eid):
    event = get_object_or_404(Event, id=eid)

    return render(request, "core/reserved_sms.html", {'event': event})


TEMP_ENTRIES = [

    {'name': 'tester', 'cell': '010-0000-0000', },

]


TEMP_ENTRIES2 = [

    {'name': 'tester', 'cell': '010-0000-0000', },

]


@login_required
def temp_sms(request):
    form = None
    sent = False

    if request.method == 'POST':
        form = SendUserSmsForm(request.POST)

        if form.is_valid():
            callees = ",".join(entry['cell'] for entry in TEMP_ENTRIES)
            sendSMS(form.cleaned_data['msg'], form.cleaned_data['caller'], callees)

            sent = True
            form = None

    if not form:
        caller = ''
        if request.user.agent:
            caller = request.user.agent.cell

        form = SendUserSmsForm(initial={'caller': caller, 'msg': '[KISP] '})

    return render(request, 'core/sms.html', {'viewname': 'event', 'entries': TEMP_ENTRIES, 'form': form, 'sent': sent})


@login_required
def temp_sms2(request):
    form = None
    sent = False

    if request.method == 'POST':
        form = SendUserSmsForm(request.POST)

        if form.is_valid():
            callees = ",".join(entry['cell'] for entry in TEMP_ENTRIES2)
            sendSMS(form.cleaned_data['msg'], form.cleaned_data['caller'], callees)

            sent = True
            form = None

    if not form:
        caller = ''
        if request.user.agent:
            caller = request.user.agent.cell

        form = SendUserSmsForm(initial={'caller': caller, 'msg': '[KISP] '})

    return render(request, 'core/sms.html', {'viewname': 'event', 'entries': TEMP_ENTRIES2, 'form': form, 'sent': sent})

