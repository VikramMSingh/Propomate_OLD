from django.test import TestCase
from django.shortcuts import reverse
# Propomate Testing

class LandingPageTest(TestCase):

	def test_get_request(self):
		response=self.client.get(reverse('home-page'))
		pass
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, "landing_page.html")

