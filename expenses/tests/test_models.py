from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Group, Expense


class GroupModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(
            name='Test Group',
            created_by=self.user
        )
        self.group.members.add(self.user)

    def test_group_creation(self):
        self.assertEqual(self.group.name, 'Test Group')
        self.assertEqual(self.group.created_by, self.user)
        self.assertTrue(self.group.members.filter(id=self.user.id).exists())