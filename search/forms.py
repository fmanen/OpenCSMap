
from django import forms

class AdvancedSearchForm(forms.Form):
    topic = forms.CharField()
    author = forms.CharField()
    show_by = forms.MultipleChoiceField()
