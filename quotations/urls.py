from django.urls import path 
from .views import InvoiceList, create_generic_invoice, viewPDF, generate_PDF

app_name = "quotations"

urlpatterns= [
path('', InvoiceList.as_view(), name="invoice-list"),
path('create/', create_generic_invoice, name="invoice-create"),
path('invoice-detail/<id>', viewPDF, name='invoice-detail'),
path('invoice-download/<id>', generate_PDF, name='invoice-download')
]