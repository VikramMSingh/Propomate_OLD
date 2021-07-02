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
from agents.views import AgentCreateView
from .forms import (LeadModelForm,
                    NewUserCreationForm, AssignAgentForm,
                    LeadCategoryUpdateForm, CategoryModelForm, FollowUpModelForm,
                    BulkUploadForm, CompanyCreationForm, EmailModelForm)
from agents.mixins import OrganizerAndLoginRequiredMixin
from csv import DictReader
import io
from .tasks import create_lead_from_file
from rest_framework.views import APIView
from rest_framework.response import Response
from propomate_crm.settings import *



logger = logging.getLogger(__name__)
# Create your views here.


class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = NewUserCreationForm

    def get_success_url(self):
        return reverse("login")

class CompanyView(generic.CreateView, OrganizerAndLoginRequiredMixin):
    template_name="registration/company_details.html"
    form_class = CompanyCreationForm

    def get_success_url(self):
        return reverse("dashboard")

    def form_valid(self, form):
        user = self.request.user
        user_profile = self.request.user.userprofile
        company = form.save(commit=False)
        company.user = user
        company.user_profile = user.userprofile
        company.save()
        return super(CompanyView, self).form_valid(form)



#class CompReg(generic.CreateView, OrganizerAndLoginRequiredMixin):
 #   template_name = 'registration/company_create.html'
  #  form_class = CompanyCreationForm 
#
 #   def get_success_url(self):
  #      return reverse("dashboard")

class ComingSoonPage(generic.CreateView):
    template_name = "collect_email.html"
    form_class = EmailModelForm 

    def get_success_url(self):
        return reverse("#")

    def form_valid(self, form):
        em = form.save(commit=True)
        em.save()
        send_mail(
            subject="A lead has been created",
            message='A new lead has been added, please review',
            from_email= EMAIL_HOST_USER,
            recipient_list= [em.email]
        )
        return super(ComingSoonPage, self).form_valid(form)

class LandingPageView(generic.TemplateView):
    def get(self, request):
        context={}
        user = self.request.user
        if request.user.is_anonymous:
            return render(request, 'landing_page.html')
        elif user.userprofile.is_first_login:
            context['firstLogin'] = 'firstLogin'
            user.userprofile.is_first_login = False
            user.userprofile.save()
            return HttpResponseRedirect(reverse('create-company'))
        else:
            return render(request, 'landing_page.html')
    
class CRMLandingPageView(generic.TemplateView):
    template_name = "landing_page.html"

    # def dispatch(self, request, *args, **kwargs):
    #	if request.user.is_authenticated:
    #		return redirect("dashboard")
    #	return super().dispatch(request, *args, **kwargs)

class ChartView(OrganizerAndLoginRequiredMixin,generic.TemplateView):
    template_name = "charts.html"

    def get_context_data(self, **kwargs):
        context = super(ChartView, self).get_context_data(**kwargs)
        user = self.request.user
        print(user.email)

        #assigned_leads = Lead.objects.filter(
       #     user_profile=user.userprofile).count()

      #  converted_category = Category.objects.get(name="Converted")
      #  converted_leads = Lead.objects.filter(
      #      user_profile=user.userprofile,
      #      category= converted_category).count()

      #  context.update({
      #      "assigned_leads":assigned_leads,
       #     "converted_leads":converted_leads
         #   })
        return context



class DashboardView(OrganizerAndLoginRequiredMixin, generic.TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        user = self.request.user

        # How many leads we have in total
        total_lead_count = Lead.objects.filter(
            user_profile=user.userprofile).count()

        # How many new leads in the last 30 days
        thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)

        total_in_past30 = Lead.objects.filter(
            user_profile=user.userprofile,
            date_added__gte=thirty_days_ago
        ).count()

        # How many converted leads in the last 30 days
        converted_category = Category.objects.get(name="Converted")

        converted_in_past30 = Lead.objects.filter(
            user_profile=user.userprofile,
            category=converted_category,
            converted_date__gte=thirty_days_ago
        ).count()
        if converted_in_past30 != 0:
            conversion_rate_30 = round((converted_in_past30/total_in_past30)*100, 3)
        else:
            conversion_rate_30=0

        ReachOut = Lead.objects.filter(
            user_profile=user.userprofile,
            agent__isnull=False,
            category__isnull=True).count()

        assigned_leads = Lead.objects.filter(
            user_profile=user.userprofile,
            agent__isnull=False).count()
        if assigned_leads != 0:
            assign_rate = round((assigned_leads/total_lead_count)*100, 3)
        else: 
            assign_rate=0

        contacted_category = Category.objects.get(name="Contacted")
        converted_leads = Lead.objects.filter(
            user_profile=user.userprofile,
            category= converted_category).count()

        if converted_leads != 0:
            conversion_rate = round((converted_leads/total_lead_count)*100, 3)
        else:
            conversion_rate=0

        contacted_leads = Lead.objects.filter(
            user_profile=user.userprofile,
            category = contacted_category).count()

        if contacted_leads != 0:
            contact_rate = round((contacted_leads/total_lead_count)*100, 3)
        else:
            contact_rate=0
  
        unconverted_category = Category.objects.get(name="Unconverted")
        unconverted_leads = Lead.objects.filter(
            user_profile=user.userprofile,
            category=unconverted_category).count()


    
        context.update({
            "total_lead_count": total_lead_count,
            "total_in_past30": total_in_past30,
            "converted_in_past30": converted_in_past30,
            "assigned_leads": assigned_leads,
            "converted_leads": converted_leads,
            "conversion_rate": conversion_rate,
            "conversion_rate_30": conversion_rate_30,
            "contacted_leads": contacted_leads,
            "contact_rate":contact_rate,
            "assign_rate":assign_rate,
            "ReachOut": ReachOut,
            "unconverted_leads": unconverted_leads,
        })
        return context


# def landing_page(request):
#	return render(request, "landing_page.html")
# Display list of leads
class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/lead_list.html"
    # user = self.request.user
    context_object_name = "leads"

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(
                user_profile=user.userprofile, agent__isnull=False)
        # if self.request.user.is_agent:
        else:
            queryset = Lead.objects.filter(
                user_profile=user.agent.user_profile, agent__isnull=False)
            # filter for current agent
            queryset = Lead.objects.filter(agent__user=user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LeadListView, self).get_context_data(**kwargs)
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(
                user_profile=user.userprofile, agent__isnull=True)
            context.update({
                "unassigned_leads": queryset
            })
        return context

# def lead_list(request):
    # return HttpResponse("This is going to be the best CRM in the world!")
#	leads = Lead.objects.all()
#	context = { "leads" : leads}
#	return render(request, "leads/lead_list.html", context)

# Detailed view of a lead


class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/lead_detail.html"
    context_object_name = "lead"

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(user_profile=user.userprofile)
        # if self.request.user.is_agent:
        else:
            queryset = Lead.objects.filter(user_profile=user.agent.user_profile)
            # filter for current agent
            queryset = Lead.objects.filter(agent__user=user)
        return queryset


# def lead_detail(request,pk):
#	lead = Lead.objects.get(id=pk)
#	context = {
#		"lead": lead
#	}
#	return render(request,"leads/lead_detail.html", context)
# Create a lead


class LeadCreateView(OrganizerAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse("leads:list-lead")

    def form_valid(self, form):
        # Send email
        user = self.request.user
        lead = form.save(commit=False)
        lead.user_profile = user.userprofile
        lead.save()
        send_mail(
            subject="A lead has been created",
            message='A new lead has been added, please review',
            from_email= EMAIL_HOST_USER,
            recipient_list= [user.email, lead.email]
        )
        messages.success(self.request, "You have successfully created a lead")
        return super(LeadCreateView, self).form_valid(form)


class BulkUploadLeads(OrganizerAndLoginRequiredMixin, generic.View):
    form = BulkUploadForm
    #template_name='leads/lead_bulk_create.html'

    #def get_success_url(self):
    #    return reverse("leads:list-lead")
    
    def get(self,request):
        template_name = 'leads/lead_bulk_create.html'
        context = {"form":BulkUploadForm}
        return render(request, template_name, context)

    def post(self,request):
        user = self.request.user
        org = self.request.user.userprofile
        paramFile = io.TextIOWrapper(request.FILES['leads_file'].file)
        portfolio = csv.DictReader(paramFile)
        list_dict=list(portfolio)
        objs = [
            Lead(
            first_name=row["first_name"],
            last_name=row["last_name"],
            age=row["age"],
            user_profile=org,
            email=row["email"],
            phone_number=row["phone_number"],
            source=row["source"]
            )
        for row in list_dict
        ]
        try:
            msg = Lead.objects.bulk_create(objs)
            returnmsg = {"status_code": 200}
            print('imported successfully')
        except Exception as e:
            print('Error While Importing Data: ',e)
            returnmsg = {"status_code": 500}
       
        return HttpResponseRedirect(reverse('leads:list-lead'))


class AutoAssignAgents(OrganizerAndLoginRequiredMixin,generic.UpdateView):
    form_class = AutoAssignForm
    
    def get(self,request):
        template_name="leads/autoAssign.html"
        user = self.request.user
        return render(request,template_name)

    def post(self, request):
        
        org = self.request.user.userprofile 
        list_agents=Agent.objects.filter(user_profile=self.request.user.userprofile)
        print(list_agents)
        #agent_list = list(list_agents)
        #agt = random.shuffle(agent_list)
        #print(agt)
        #agt = random.shuffle(agent_list)
        leads_list=Lead.objects.filter(category__isnull=True, agent__isnull=True, user_profile=org)
        for lead in leads_list:
            try:
                #rend=random.shuffle(agent_list)
                rnd = random.choice(list_agents.order_by('?'))
               # print(rnd)
                msg = leads_list.update(agent=rnd)
                returnmsg = {"status_code": 200}
                #print('imported successfully')
            except Exception as e:
                print('Error While Importing Data: ',e)
                returnmsg = {"status_code": 500}
            #return reverse("leads:list-lead")

        return HttpResponseRedirect(reverse('leads:list-lead'))
            
        
            
            



# #def lead_create(request):
#	form = LeadModelForm()
#	if request.method=="POST":
    # print("Post req received")
#		form = LeadModelForm(request.POST)
####
# context = {
#		"form": LeadModelForm()
#	}
#	return render(request,"leads/lead_create.html", context)

# Update or modify a lead

class LeadUpdateView(OrganizerAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/update_lead.html"
    # queryset = Lead.objects.all()
    form_class = LeadModelForm

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(user_profile=user.userprofile)
        return queryset

    def get_success_url(self):
        return reverse("leads:list-lead")

# def update_lead(request,pk):
#	lead = Lead.objects.get(id=pk)
#	form = LeadModelForm(instance=lead)
    # ^ will only update the lead, not create or modify others
#	if request.method=="POST":
#		if form.is_valid():
#			form.save()
#			return redirect("/leads")
#	context = {
#		"form": form,
#		"lead": lead
#	}
#	return render(request, "leads/update_lead.html", context)

# Delete a lead


class LeadDeleteView(OrganizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/delete_lead.html"
    # queryset = Lead.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Lead.objects.filter(user_profile=user.userprofile)
        return queryset

    def get_success_url(self):
        return reverse("leads:list-lead")
# def delete_lead(request,pk):
#	lead = Lead.objects.get(id=pk)
#	lead.delete()
#	return redirect("/leads")


class AssignAgentView(OrganizerAndLoginRequiredMixin, generic.FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm

# For passing extra arguments to form
    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "request": self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse("leads:list-lead")

    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)


class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user
        #converted_category = Category.objects.get(name="Converted")
        if user.is_organizer:
            queryset = Lead.objects.filter(user_profile=user.userprofile)
        # if self.request.user.is_agent:
        else:
            queryset = Lead.objects.filter(user_profile=user.agent.user_profile)

        context.update({
            "unassigned_lead_count": queryset.filter(category__isnull=True).count(),
            #"converted_count": queryset.filter(category=converted_category).count()

        })
        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Category.objects.filter(user_profile=user.userprofile)
        # if self.request.user.is_agent:
        else:
            queryset = Category.objects.filter(
                user_profile=user.agent.userprofile)
        return queryset


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    # def get_context_data(self, **kwargs):
    #	context=super(CategoryDetailView, self).get_context_data(**kwargs)
    #	user = self.request.user
    #	Lead.object.filter(category=self.get_object())
#	context.update({
    #		"unassigned_lead_count": queryset.filter(category__isnull=True).count()
    #		})
    #	return context

    def get_queryset(self):
        user = self.request.user
        if user.is_organizer:
            queryset = Category.objects.filter(user_profile=user.userprofile)
        # if self.request.user.is_agent:
        else:
            queryset = Category.objects.filter(
                user_profile=user.agent.user_profile)
        return queryset


class CategoryCreateView(OrganizerAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/category_create.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse("leads:category-list")

    def form_valid(self, form):
        category = form.save(commit=False)
        category.user_profile = self.request.user.userprofile
        category.save()
        return super(CategoryCreateView, self).form_valid(form)


class CategoryUpdateView(OrganizerAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/category_update.html"
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse("leads:category-list")

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organizer:
            queryset = Category.objects.filter(
                user_profile=user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                user_profile=user.agent.organisation
            )
        return queryset


class CategoryDeleteView(OrganizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/category_delete.html"

    def get_success_url(self):
        return reverse("leads:category-list")

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organizer:
            queryset = Category.objects.filter(
                user_profile=user.userprofile
            )
        else:
            queryset = Category.objects.filter(
                user_profile=user.agent.userprofile
            )
        return queryset


class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organizer:
            queryset = Lead.objects.filter(user_profile=user.userprofile)
        else:
            queryset = Lead.objects.filter(
                user_profile=user.agent.user_profile)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_success_url(self):
        return reverse("leads:detail-view", kwargs={"pk": self.get_object().id})

    def form_valid(self, form):
        lead_before_update = self.get_object()
        instance = form.save(commit=False)
        converted_category = Category.objects.get(name="Converted")
        if form.cleaned_data["category"] == converted_category:
            # update the date at which this lead was converted
            if lead_before_update.category != converted_category:
                # this lead has now been converted
                instance.converted_date = datetime.datetime.now()
        instance.save()
        return super(LeadCategoryUpdateView, self).form_valid(form)


class FollowUpCreateView(LoginRequiredMixin, generic.CreateView):
    template_name = "leads/followup_create.html"
    form_class = FollowUpModelForm

    def queryset(self):
        user=self.request.user

        if user.is_organizer:
            queryset = Lead.objects.filter(user_profile=user.userprofile)
        else:
            queryset = Lead.objects.filter(
                user_profile=user.agent.user_profile)
            # filter for the agent that is logged in
            queryset = queryset.filter(agent__user=user)
        return user, queryset

    def get_success_url(self):
        return reverse("leads:detail-view", kwargs={"pk": self.kwargs["pk"]})

    def get_context_data(self, **kwargs):
        context = super(FollowUpCreateView, self).get_context_data(**kwargs)
        context.update({
            "lead": Lead.objects.get(pk=self.kwargs["pk"])
        })
        return context


    def form_valid(self, form):
        lead = Lead.objects.get(pk=self.kwargs["pk"])
        followup = form.save(commit=False)
        followup.user = self.request.user
        followup.lead = lead
        followup.save()
        send_mail(
            subject="Update on your status",
            message="Follow up added to your status",
            from_email= EMAIL_HOST_USER,
            recipient_list= [ followup.lead.email ] 
        )
        messages.success(self.request, "A note has been added")
        return super(FollowUpCreateView, self).form_valid(form)


class FollowUpUpdateView(OrganizerAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/followup_update.html"
    form_class = FollowUpModelForm

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organizer:
            queryset = FollowUp.objects.filter(
                lead__user_profile=user.userprofile)
        else:
            queryset = FollowUp.objects.filter(
                lead__user_profile=user.agent.user_profile)
            # filter for the agent that is logged in
            queryset = queryset.filter(lead__agent__user=user)
        return queryset

    def get_success_url(self):
        return reverse("leads:detail-view", kwargs={"pk": self.get_object().lead.id})


class FollowUpDeleteView(OrganizerAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/followup_delete.html"

    def get_success_url(self):
        followup = FollowUp.objects.get(id=self.kwargs["pk"])
        return reverse("leads:detail-view", kwargs={"pk": followup.lead.pk})

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organizer:
            queryset = FollowUp.objects.filter(
                lead__user_profile=user.userprofile)
        else:
            queryset = FollowUp.objects.filter(
                lead__user_profile=user.agent.organisation)
            # filter for the agent that is logged in
            queryset = queryset.filter(lead__agent__user=user)
        return queryset

class LeadJsonView(generic.View):

    def get(self, request, *args, **kwargs):

        qs = list(Lead.objects.all().values(
            "first_name",
            "last_name",
            "age")
        )

        return JsonResponse({
            "qs": qs,
        })

class LeadLearnView(LoginRequiredMixin,generic.TemplateView):
    template_name="learning/leads_how_to.html"


