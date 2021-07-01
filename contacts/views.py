import csv
import logging
import datetime
import random
from django.contrib import messages
from agents.forms import AutoAssignForm
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from .models import *
from agents.mixins import OrganizerAndLoginRequiredMixin
from .forms import ContactModelForm

# Create your views here.
class ContactListView(generic.ListView, LoginRequiredMixin):
	template_name = "contacts/contact_list.html"
	context_object_name = "contacts"

	def get_queryset(self):
		user = self.request.user
		queryset = Contact.objects.filter(user_profile=user.userprofile)
		return queryset

	def context_data(self, **kwargs):
		context = super(ContactListView,self).get_context_data(**kwargs)
		user = self.request.user
		
		return context


class ContactCreateView(generic.CreateView, OrganizerAndLoginRequiredMixin):
	template_name ="contacts/contact_create.html"
	form_class = ContactModelForm

	def get_success_url(self):
		return reverse("contacts:contact-list")

	def form_valid(self,form):
		user = self.request.user
		contact = form.save(commit=False)
		contact.user_profile = user.userprofile
		contact.save()
		return super(ContactCreateView, self).form_valid(form)

class ContactDetailView(generic.DetailView, LoginRequiredMixin):
	template_name = "contacts/contact_detail.html"
	context_object_name = "contact"

	def get_queryset(self):
		user = self.request.user
		queryset = Contact.objects.filter(user_profile = user.userprofile)
		return queryset 

class UpdateContactView(generic.UpdateView, OrganizerAndLoginRequiredMixin):
	template_name="contacts/update_contact.html"
	form_class = ContactModelForm

	def get_queryset(self):
		user = self.request.user
		if user.is_organizer:
			queryset = Contact.objects.filter(user_profile=user.userprofile)
		return queryset

		def get_success_url(self):
			return reverse("contacts:contact-list")

class ContactDeleteView(generic.DeleteView, OrganizerAndLoginRequiredMixin):
	template_name = "contacts/delete_contact.html"

	def get_queryset(self):
		user = self.request.user
		if user.is_organizer:
			queryset = Contact.objects.filter(user_profile=user.userprofile)
		return queryset

	def get_success_url(self):
		return reverse("contacts:contact-list")
		

