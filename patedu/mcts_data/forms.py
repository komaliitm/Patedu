# -*- coding: utf-8 -*-
from django import forms

class Document(forms.Form):
    image = forms.FileField(
        label='Select a file'
    )