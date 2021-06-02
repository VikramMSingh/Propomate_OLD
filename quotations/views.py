import csv
import logging
import datetime
import random
from django.contrib import messages
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from .models import *
from agents.mixins import OrganizerAndLoginRequiredMixin
from .forms import * 
from leads.models import *
# Create your views here.

class InvoiceList(generic.ListView, LoginRequiredMixin):
	template_name = 'invoice/generic_invoices.html'
	def get(self, *args, **kwargs):
		user = self.request.user
		invoices = Invoice.objects.filter(user_profile=user.userprofile)
		context = {
		"invoices":invoices,
		}
		return render(self.request,'invoice/generic_invoices.html', context)

def create_generic_invoice(request):
	Mp = Company.objects.get(user_profile=request.user.userprofile)
	print(Mp)

	if request.method == "GET":
		formset = LineItemFormset(request.GET or None)
		form = InvoiceForm(request.GET or None)
	elif request.method == "POST":
		formset = LineItemFormset(request.POST)
		form = InvoiceForm(request.POST)
		

		if form.is_valid():
			invoice = Invoice.objects.create(
				user = request.user,
				user_profile=request.user.userprofile,
				company = Mp,
				customer=form.data["customer"],
				customer_email = form.data["customer_email"],
				billing_address = form.data["billing_address"],
				date = form.data["date"],
				due_date = form.data["due_date"]
				)

		if formset.is_valid():
			#user = self.request.user
			total = 0 
			for form in formset:
				service = form.cleaned_data.get('service')
				description = form.cleaned_data.get('description')
				quantity = form.cleaned_data.get('quantity')
				rate = form.cleaned_data.get('rate')

				if service and description and quantity and rate:
					amount = float(rate)*float(quantity)
					total += amount
					LineItem(user = request.user,
						user_profile = request.user.userprofile,
						company=Mp,
						customer=invoice,
						service=service,
						description=description,
						quantity=quantity,
						rate=rate,
						amount=amount).save()
			invoice.total_amount = total
			invoice.save()
			return redirect('/')
			try:
				generate_PDF(request, id=invoice.id)
			except Exception as e:
				print(f"********{e}********")
			return redirect('/')
	context = {
				"title": "Invoice",
				"formset": formset,
				"form": form,
			}
	return render(request,'invoice/generic_invoice_create.html', context)


def viewPDF(request,id=None):
	invoice = get_object_or_404(Invoice,id=id)
	line_item = invoice.lineitem_set.all()
	print(request.user.userprofile)
	Mp = Company.objects.get(user_profile=request.user.userprofile)

	context = {
		"company": {
		"name": Mp.company_name,
		"address": Mp.company_address,
		"phone": "+91 9820433098",
		"email": "xyz@propomate.com"
		},
		"invoice_id":invoice.id,
		"invoice_total": invoice.total_amount,
		"customer": invoice.customer,
		"customer_email": invoice.customer_email,
		"date": invoice.date,
		"due_date": invoice.due_date,
		"billing_address": invoice.billing_address,
		"lineitem": line_item 
	}
	return render(request, "invoice/pdf_template.html", context)

def generate_PDF(request, id):
 ##  response = HttpResponse(pdf,content_type='application/pdf')
   # response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

    return response