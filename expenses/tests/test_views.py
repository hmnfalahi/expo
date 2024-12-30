from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Group


class GroupViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_dashboard_view(self):
        response = self.client.get(reverse('expenses:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'expenses/dashboard.html')