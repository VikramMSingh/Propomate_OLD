import logging
import datetime
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse
from django.http import HttpResponse
from django.views import generic
from .models import *
from agents.views import AgentCreateView
from .forms import (LeadModelForm,
                    NewUserCreationForm, AssignAgentForm,
                    LeadCategoryUpdateForm, CategoryModelForm, FollowUpModelForm,
                    BulkUploadForm)
from agents.mixins import OrganizerAndLoginRequiredMixin
from csv import DictReader

def create_lead_from_file(validated_rows, invalid_rows, user_id, source, company_id):
    """Parameters : validated_rows, invalid_rows, user_id.
    This function is used to create leads from a given file.
    """
    email_regex = "^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,4})$"
    user = self.request.user
    company = Lead.objects.filter(user_profile=user.userprofile).first()
    for row in validated_rows:
        if not Lead.objects.filter(title=row.get("title")).exists():
            if re.match(email_regex, row.get("email")) is not None:
                try:
                    lead = Lead()
                    lead.first_name = row.get("first name", "")[:255]
                    lead.last_name = row.get("last name", "")[:255]
                    lead.email = row.get("email", "")
                    lead.phone_number = row.get("phone_number", "")
                    lead.description = row.get("description", "")
                    lead.user_profile = user.userprofile
                    lead.source = row.get("source","")
                    lead.save()
                except Exception as e:
                    print(e)