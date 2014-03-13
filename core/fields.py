# -*- coding:utf-8 -*-
from django.db import models
from django.forms import MultipleChoiceField,CheckboxSelectMultiple
from django.forms.widgets import SelectMultiple
from djangotoolbox.fields import ListField

class FormListField(MultipleChoiceField):
    widget = CheckboxSelectMultiple
    native = True

    def __init__(self, model=None, order_by='pk', *args, **kwargs):
        self._model = model
        super(FormListField, self).__init__(*args, **kwargs)
        
        self.widget.choices = [(str(i.pk), i) for i in self._model.objects.all().order_by(order_by)]

    def to_python(self, value):
        return [self._model.objects.get(pk=key) for key in value]

    def clean(self, value):
        return value

class ModelListField(ListField):
    def __init__(self, embedded_model=None, order_by='pk', *args, **kwargs):
        super(ModelListField, self).__init__(*args, **kwargs)
        self._model = embedded_model
        self._order_by = order_by

    def formfield(self, **kwargs):
        return FormListField(model=self._model, order_by=self._order_by, **kwargs)

