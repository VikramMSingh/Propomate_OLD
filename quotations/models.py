from django.db import models
from leads.models import User, UserProfile, Lead, Company
import datetime
# Create your models here.


class Invoice(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='comp_name')
	customer = models.CharField(max_length=100)
	customer_email = models.EmailField(null=True, blank=True)
	billing_address = models.TextField(null=True, blank=True)
	date = models.DateField()
	due_date = models.DateField(null=True, blank=True)
	#message = models.TextField(default= "this is a default message.")
	total_amount = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
	status = models.BooleanField(default=False)
	def __str__(self):
	    return str(self.user)

	def get_status(self):
		return self.status

    # def save(self, *args, **kwargs):
        # if not self.id:             
        #     self.due_date = datetime.datetime.now()+ datetime.timedelta(days=15)
        # return super(Invoice, self).save(*args, **kwargs)

class LineItem(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='comp_name_li')
	customer = models.ForeignKey(Invoice, on_delete=models.CASCADE)
	service = models.TextField()
	description = models.TextField()
	quantity = models.IntegerField()
	rate = models.DecimalField(max_digits=9, decimal_places=2)
	amount = models.DecimalField(max_digits=9, decimal_places=2)

	def __str__(self):
	    return str(self.user)
