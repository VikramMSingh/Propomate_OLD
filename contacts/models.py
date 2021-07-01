from django.db import models
from django.db.models.signals import post_save
from leads.models import User, UserProfile

#Create models
class Contact(models.Model):
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	email = models.EmailField(unique=True)
	phone = models.CharField(null=True, unique=True, max_length=10)
	organization = models.CharField(max_length=255, null=True)
	title = models.CharField(max_length=255, null=True)
	description = models.CharField(max_length=500, null=True, blank=True)
	user_profile = models.ForeignKey(UserProfile, related_name="contact_user_profile", on_delete=models.CASCADE)
	profile_picture = models.ImageField(null=True, blank=True,upload_to="profile_pictures/")
	created_on = models.DateTimeField( auto_now_add=True )
	created_by = models.ForeignKey(User, related_name="create_by", on_delete=models.CASCADE, null=True)

	def __str__(self):
		return self.first_name

	class Meta:
		ordering = ["-created_on"]