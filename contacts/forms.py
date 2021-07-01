from django import forms
from django.forms import formset_factory
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Contact

class ContactModelForm(forms.ModelForm):
	class Meta:
		model = Contact
		fields = (
			'first_name',
			'last_name',
			'email',
			'phone',
			'organization',
			'title',
			'description',
			'profile_picture')

	def clean_first_name(self):
		data = self.cleaned_data["first_name"]
		return data

	def clean_email(self):
		data = self.cleaned_data["email"]
		if Contact.objects.filter(email=data).exists():
			raise ValidationError("Contact already exists")
		return data

	def clean(self):
		pass

    	