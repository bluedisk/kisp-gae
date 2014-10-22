# -*- coding:utf-8 -*-
from django import forms
from core.models import Entry, Agent, EventImage, Feedback
from captcha.fields import ReCaptchaField
from django.contrib.auth.models import User

from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth import authenticate, get_user_model

import re

from core.utils import *

MAXIMUM_PASSWORD_LENGTH = 256


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['name', 'cell', 'regnum', 'club', 'htype', 'hdist', 'tsize', 'mileage', 'etc', 'carpool', 'location', 'skill']
        native_fields = ['skill', 'course']

    captcha = ReCaptchaField()

    def clean_regnum(self):
        return format_regnum(self.data['regnum'])

    def clean_cell(self):
        cell = self.cleaned_data['cell']
        cell = format_cell(cell)

        return cell


class AgentEntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['name', 'cell', 'regnum', 'club', 'htype', 'hdist', 'tsize', 'mileage', 'etc', 'carpool', 'location', 'skill']
        native_fields = ['skill']

    def clean_cell(self):
        cell = self.cleaned_data['cell']
        cell = format_cell(cell)

        return cell

    def clean_regnum(self):
        return format_regnum(self.data['regnum'])


class SendSmsForm(forms.Form):
    caller = forms.CharField(max_length=14, required=True)
    msg = forms.CharField(max_length=80, required=True)
    captcha = ReCaptchaField()


class SendUserSmsForm(forms.Form):
    caller = forms.CharField(max_length=14, required=True)
    msg = forms.CharField(max_length=80, required=True)


class UserSignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']

    username = forms.CharField(
        required=True,
        label=_(u"아이디")
    )

    first_name = forms.CharField(
        required=True,
        label=_(u"이름(실명)")
    )

    email = forms.EmailField(
        required=True,
        label=_(u"이메일 주소")
    )

    password1 = forms.CharField(
        required=True,
        label=_(u"비밀번호"),
        widget=forms.PasswordInput,
        max_length=MAXIMUM_PASSWORD_LENGTH,
    )
    password2 = forms.CharField(
        required=True,
        label=_(u"비밀번호 확인"),
        widget=forms.PasswordInput,
        max_length=MAXIMUM_PASSWORD_LENGTH,
    )

    def clean_username(self):

        if User.objects.filter(username=self.cleaned_data.get('username')).count():
            raise forms.ValidationError(u"이미 존재하는 아이디입니다.")

        return self.data['username']

    def clean_password1(self):

        password1 = self.data['password1']
        password2 = self.data['password2']

        if password1 != password2:
            raise forms.ValidationError(u"")

        return self.data['password1']

    def clean_password2(self):

        password1 = self.data['password1']
        password2 = self.data['password2']

        if password1 != password2:
            raise forms.ValidationError(u"새 비밀번호와 확인이 일치하지 않습니다.")

        return self.data['password2']

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserSignupForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        required=True,
        label=_("기존 비밀번호"),
        widget=forms.PasswordInput,
        max_length=MAXIMUM_PASSWORD_LENGTH,
    )

    password1 = forms.CharField(
        required=True,
        label=_("비밀번호"),
        widget=forms.PasswordInput,
        max_length=MAXIMUM_PASSWORD_LENGTH,
    )
    password2 = forms.CharField(
        required=True,
        label=_("비밀번호 확인"),
        widget=forms.PasswordInput,
        max_length=MAXIMUM_PASSWORD_LENGTH,
    )

    def clean(self):
        user = authenticate(request.user.username, old_password)

        if not user:
            raise forms.ValidationError(u"기존 비밀번호가 일치하지 않습니다.")

        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 != password2:
            raise forms.ValidationError(u"새 비밀번호와 확인이 일치하지 않습니다.")

        return self.cleaned_data


class UserSigninForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(max_length=254)
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput,
        max_length=MAXIMUM_PASSWORD_LENGTH,
    )

    error_messages = {
        'invalid_login': _("Please enter a correct %(username)s and password. "
                           "Note that both fields may be case-sensitive."),
        'no_cookies': _("Your Web browser doesn't appear to have cookies "
                        "enabled. Cookies are required for logging in."),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super(UserSigninForm, self).__init__(*args, **kwargs)

        # Set the label for the "username" field.
        UserModel = get_user_model()
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        if not self.fields['username'].label:
            self.fields['username'].label = u"아이디"

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'] % {
                        'username': self.username_field.verbose_name
                    })
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['cell', 'regnum', 'mileage', 'tsize', 'image', 'skill', 'location']
        native_fields = ['image', 'skill']

    def clean_cell(self):
        cell = self.cleaned_data['cell']
        cell = format_cell(cell)

        return cell

    def clean_regnum(self):
        return format_regnum(self.data['regnum'])


class EventImageForm(forms.ModelForm):
    class Meta:
        model = EventImage
        fields = ['title', 'image', 'featured']
        native_fields = ['image', 'featured']


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'event', 'regnum', 'where', 'spend', 'patient', 'report', 'suggest']
        widgets = {
            'event': forms.HiddenInput,
        }

    spend = forms.CharField(label=u'사용 금액')
    uid = forms.IntegerField(label=u'User ID')

    def clean_name(self):
        name = self.data['name']
        regnum = format_regnum(self.data['regnum'])
        event = self.data['event']

        try:
            Entry.objects.get(event=event, name=name, regnum=regnum)
        except:
            raise forms.ValidationError(u'참가자중에 일치하는 대원 정보가 없습니다.')

        return name

    def clean_regnum(self):
        return format_regnum(self.data['regnum'])

    def clean_spend(self):
        spend = self.cleaned_data['spend']
        spend = int(re.sub('[^0-9]', '', spend))

        return spend

    def clean_where(self):
        where = self.cleaned_data['where']
        spend = self.data['spend']
        spend = re.sub('[^0-9]', '', spend) or '0'
        spend = int(spend)

        if spend != 0 and not where:
            raise forms.ValidationError(u'해당 금액을 사용한 내역 입력이 필요합니다.')

        return where
