from django import forms
#from leads.models import Agent 
from django.contrib.auth import get_user_model
from .main_forms import UserCreationForm

User = get_user_model()

class AgentModelForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('email',
			'username',
			'first_name',
			'last_name'
			)

class SelfAgentForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('email',
			'first_name',
			'last_name')

class AutoAssignForm(forms.Form):
	confirm_field = forms.CharField()
			