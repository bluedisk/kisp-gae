# -*- coding:utf-8 -*-
from django import template
from core.models import Page

register = template.Library()

@register.simple_tag
def render_page(page_code):
	try:
		page = Page.objects.get(pk=page_code)
		return '<div class="head-pager"><h3>%s<small>%s</small></h3></div><hr><div class="container">%s</div>'%(page.title, page.subtitle, page.content)
	except:
		return u'지정한 페이지가 없습니다.'

@register.assignment_tag
def get_page(page_code):
	try:
		page = Page.objects.get(pk=page_code)
		return page
	except:
		return {'title':u'지정한 페이지가 없습니다.', 'subtitle':'', 'content':''}
