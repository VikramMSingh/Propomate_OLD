#urls.py 
from django.urls import path 
from .views import (
	LeadListView, LeadDetailView, LeadCreateView, 
	LeadUpdateView, LeadDeleteView, AssignAgentView,
	CategoryListView, CategoryDetailView, LeadCategoryUpdateView,
	CategoryCreateView, CategoryUpdateView, CategoryDeleteView, LeadJsonView,
	FollowUpCreateView, FollowUpUpdateView, FollowUpDeleteView, BulkUploadLeads,
	AutoAssignAgents, ChartView)

app_name = "leads"

urlpatterns = [
	path('',LeadListView.as_view(), name='list-lead'),
	path('create/',LeadCreateView.as_view(), name='create-lead'),
	path('bulk_create/',BulkUploadLeads.as_view(),name="bulk-create-lead"),
	path('<int:pk>/', LeadDetailView.as_view(), name='detail-view'),
	path('<int:pk>/update/',LeadUpdateView.as_view(),name='update-lead'),
	path('<int:pk>/delete/',LeadDeleteView.as_view(),name='delete-lead'),
	path('<int:pk>/assign-agent/', AssignAgentView.as_view(),name='assign-agent'),
	path('categories/', CategoryListView.as_view(), name="category-list"),
	path('categories/<int:pk>/', CategoryDetailView.as_view(), name="category-detail"),
	path('<int:pk>/category/', LeadCategoryUpdateView.as_view(), name='lead-category-update'),
	path('json/', LeadJsonView.as_view(), name='lead-list-json'),
	path('<int:pk>/followups/create/', FollowUpCreateView.as_view(), name='lead-followup-create'),
	path('followups/<int:pk>', FollowUpUpdateView.as_view(), name='lead-followup-update'),
	path('followups/<int:pk>/delete/', FollowUpDeleteView.as_view(), name='lead-followup-delete'),
	path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),
	path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
	path('create-category/', CategoryCreateView.as_view(), name='category-create'),
	path('auto-assign/',AutoAssignAgents.as_view(), name='auto-assign')
	]