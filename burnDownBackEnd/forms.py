from django import forms
from .models import Company, Team, Sprint
from django.forms import ModelForm
#class NameForm(forms.Form):
#    your_name = forms.CharField(label='Your name', max_length=100)

class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ['name']

class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = ['name','company']

class SprintForm(ModelForm):
    class Meta:
        model = Sprint
        fields = ['start_date','end_date','team','goal']
