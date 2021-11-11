"""propomate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import (LoginView, LogoutView, 
    PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView,
    PasswordResetCompleteView)
from django.urls import path, include
from leads.views import (ComingSoonPage, LandingPageView, SignupView, DashboardView, LeadLearnView, ChartView, CompanyView)

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', ComingSoonPage.as_view(), name='coming-soon'),
    path('', LandingPageView.as_view() , name='home-page'),
    #path('continue-registration/', CompReg.as_view(), name="company_register"),
    path('dashboard/', DashboardView.as_view(), name="dashboard"),
    path('company_details/', CompanyView.as_view(), name="create-company"),
    path('login/',LoginView.as_view(), name='login'),
    path('reset-password/', PasswordResetView.as_view(), name='reset-password'),
    path('password-reset-done/',PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/',LogoutView.as_view(), name='logout'),
    path('signup/',SignupView.as_view(),name='signup'),
    path('learning/leads',LeadLearnView.as_view(), name="learn-lead"),
    path('charts/',ChartView.as_view(), name='charts'),
 	path('leads/', include('leads.urls', namespace="leads")),
    path('agents/',include('agents.urls', namespace='agents')),
    path('invoicing/',include('quotations.urls', namespace='invoicing')),
    path('contacts/',include('contacts.urls',namespace='contacts'))
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
