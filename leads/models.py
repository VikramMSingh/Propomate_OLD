from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail, EmailMultiAlternatives

# Create your models here.


class User(AbstractUser):
	is_organizer = models.BooleanField(default=True)
	is_agent = models.BooleanField(default=False)


class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	is_first_login = models.BooleanField(default=True)

	def __str__(self):
		return self.user.username


#class UserAccount(models.Model):
#	user = models.ForeignKey(User,related_name="user_account", on_delete=models.CASCADE)
#	user_profile = models.ForeignKey(UserProfile, related_name="user_prof", on_delete=models.CASCADE)
#	user_company = models.CharField(max_length=100)
#	user_company_address = models.CharField(max_length = 1000)
#	user_website = models.CharField(max_length=50)

#	def __str__(self):
#		return self.user.user_company

class Company(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	user_profile = models.ForeignKey(UserProfile, related_name='user_profile_company', on_delete=models.CASCADE)
	company_name = models.CharField(max_length=40, null=True)
	company_address = models.CharField(max_length=1000, null=True)
	company_phone = models.CharField(max_length=13, null=True)
	company_website= models.CharField(max_length=100, null=True)
	company_logo = models.ImageField(null=True, blank=True, upload_to="company_logo/")

	def __str__(self):
		return self.company_name

class Email(models.Model):
	email = models.EmailField(null=True, blank=True)


class LeadManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()


class Lead(models.Model):
	first_name = models.CharField(max_length=20)
	last_name = models.CharField(max_length=20)
	age = models.IntegerField(default=0)
	user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	agent = models.ForeignKey(
	    "Agent", null=True, blank=True, on_delete=models.SET_NULL)
	category = models.ForeignKey(
	    "Category", related_name="leads", null=True, blank=True, on_delete=models.SET_NULL)
	description = models.TextField()
	date_added = models.DateTimeField(auto_now_add=True)
	phone_number = models.CharField(max_length=13)
	email = models.EmailField()
	profile_picture = models.ImageField(
	    null=True, blank=True, upload_to="profile_pictures/")
	converted_date = models.DateTimeField(null=True, blank=True)
	source = models.CharField(max_length=100, null=True, blank=True)

	objects = LeadManager()

	def __str__(self):
		return f"{self.first_name} {self.last_name}"

#class Lead_Invoice(models.Model):
#	user = models.ForeignKey(User, related_name='user_lead_invoice', on_delete=models.CASCADE)
#	user_profile = models.ForeignKey(UserProfile, related_name='user_profile_invoice', on_delete=models.CASCADE)
#	lead = models.ForeignKey(Lead, related_name="invoice_lead", on_delete=models.CASCADE)
#	company = models.ForeignKey(Company, related_name="invoice_company", on_delete=models.CASCADE)
#	date = models.DateField()
#	due_date = models.DateField(null=True, blank=True)
#	total_amount = models.DecimalField(max_digits=9, decimal_places=2)
#	status = models.BooleanField(default=False)

#	def __str__(self):
#		return str(self.user)

#	def get_status(self):
#		return self.status

#class Lead_Line_Item(models.Model):
#	user = models.ForeignKey(User, related_name="user_line_item", on_delete=models.CASCADE)
#	user_profile = models.ForeignKey(UserProfile, related_name='user_profile_line_item', on_delete=models.CASCADE)
#	lead = models.ForeignKey(Lead, related_name='lead_line_item', on_delete=models.CASCADE)
#	company = models.ForeignKey(Company, related_name='line_item_company', on_delete=models.CASCADE)
#	service = models.TextField()
#	description = models.TextField()
#	quantity = models.IntegerField()
#	rate = models.DecimalField(max_digits=9, decimal_places=2)
#	amount = models.DecimalField(max_digits=9, decimal_places=2)

#	def __str__(self):
#		return str(self.user)


def handle_upload_follow_ups(instance, filename):
    return f"lead_followups/lead_{instance.lead.pk}/{filename}"


class FollowUp(models.Model):
	user = models.ForeignKey(User, related_name="user_followup", on_delete=models.CASCADE)
	lead = models.ForeignKey(Lead, related_name="followups", on_delete=models.CASCADE)
	date_added = models.DateTimeField(auto_now_add=True)
	notes = models.TextField(blank=True, null=True)
	file = models.FileField(null=True, blank=True,upload_to=handle_upload_follow_ups)
	
	def __str__(self):
		return f"{self.lead.first_name} {self.lead.last_name}"


class Agent(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

	def __str__(self):
		return self.user.email


class Category(models.Model):
	name = models.CharField(max_length=30)
	user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

	def __str__(self):
		return self.name

#class InvoiceLeads(models.Model):
#	user = models.ForeignKey(User, on_delete=models.CASCADE)
#	user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
#	lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
	#customer = models.CharField(max_length=100)
	#customer_email = models.EmailField(null=True, blank=True)
#	billing_address = models.TextField(null=True, blank=True)
#	date = models.DateField()
	#due_date = models.DateField(null=True, blank=True)
	#message = models.TextField(default= "this is a default message.")
	#total_amount = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
	#status = models.BooleanField(default=False)
	#def __str__(self):
	#    return str(self.user)

	#def get_status(self):
	#	return self.status

def post_user_signal(sender,instance,created, **kwargs):
	if created:
		UserProfile.objects.create(user=instance )
		Agent.objects.create(user=instance, user_profile=instance.userprofile)

post_save.connect(post_user_signal, sender=User)

def post_email_signal(sender,instance,created,**kwargs):
	if created:
		subject = "Test Email"
		message = "Create beautiful landing pages, automate your marketing emails and messages."
		cust = instance
		send_mail(
			subject,
			message,
			from_email= EMAIL_HOST_USER,
			recipient_list = [cust]
			)
post_save.connect(post_email_signal, sender=Email)
