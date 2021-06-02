
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

class OrganizerAndLoginRequiredMixin(AccessMixin):
	#Verify if user is logged in and is organizer

	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_authenticated or not request.user.is_organizer:
			return redirect("leads:list-lead")
		return super().dispatch(request, *args, **kwargs)

		
	


