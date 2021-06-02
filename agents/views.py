from django.shortcuts import render, reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from leads.models import Agent
from .forms import AgentModelForm, SelfAgentForm
from .mixins import OrganizerAndLoginRequiredMixin
from django.core.mail import send_mail
import random 

# Create your views here.
class AgentListView(OrganizerAndLoginRequiredMixin,generic.ListView):
	template_name = "agents/agent_list.html"

	def get_queryset(self):
		org = self.request.user.userprofile
		return Agent.objects.filter(user_profile=org)

class SelfAgentCreateView(OrganizerAndLoginRequiredMixin, generic.CreateView):
	template_name = "agents/self_agent_create.html"
	form_class = SelfAgentForm

	def get_success_url(self):
		return reverse("agents:agent-list")

	def form_valid(self,form):
		Agent.objects.create(
			user=self.request.user,
			user_profile=self.request.user.userprofile
			)
		return super(SelfAgentCreateView,self).form_valid(form)

class AgentCreateView(OrganizerAndLoginRequiredMixin,generic.CreateView):
	template_name = "agents/agent_create.html"
	form_class = AgentModelForm

	def get_success_url(self):
		return reverse("agents:agent-list")

	def form_valid(self,form):
		user = form.save(commit=False)
		user.is_agent = True
		user.is_organizer = False
		user.set_password(f"{random.randint(0, 100000)}")
		user.save()
		Agent.objects.create(
			user=user,
			user_profile=self.request.user.userprofile
			)
		send_mail(
			subject="You are invited to be a teammate",
			message = "You are invited by {{ user.first_name }} to join his organization on Propomate",
			from_email="test@test.com",recipient_list=["vikrammsingh11@gmail.com"]
			)
		return super(AgentCreateView,self).form_valid(form)

class AgentDetailView(OrganizerAndLoginRequiredMixin,generic.DetailView):
	template_name = "agents/agent_detail.html"
	context_object_name = "agent"

	def get_queryset(self):
		org = self.request.user.userprofile
		return Agent.objects.filter(user_profile=org)

class AgentUpdateView(OrganizerAndLoginRequiredMixin,generic.UpdateView):
	template_name = "agents/agent_update.html"
	#context_object_name = "agent"
	form_class = AgentModelForm

	def get_queryset(self):
		org = self.request.user.userprofile
		return Agent.objects.filter(user_profile=org)

	def get_success_url(self):
		return reverse("agents:agent-list")

class AgentDeleteView(OrganizerAndLoginRequiredMixin,generic.DeleteView):
	template_name = "agents/agent_delete.html"
	context_object_name = "agent"

	def get_queryset(self):
		org = self.request.user.userprofile
		return Agent.objects.filter(user_profile=org)

	def get_success_url(self):
		return reverse("agents:agent-list")



