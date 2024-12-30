from django.db import models
from django.contrib.auth.models import User
import uuid


class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='expense_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_groups'
    )
    join_code = models.UUIDField(default=uuid.uuid4, unique=True)
    sessions = models.ManyToManyField('Session', related_name='group_sessions', blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_total_expenses(self):
        """Calculate total expenses for the group"""
        return self.expenses.aggregate(
            total=models.Sum('amount')
        )['total'] or 0.00

    def get_member_count(self):
        """Get number of members in the group"""
        return self.members.count()

    def add_member(self, user):
        """Add a member to the group"""
        self.members.add(user)

    def remove_member(self, user):
        """Remove a member from the group"""
        if user != self.created_by:
            self.members.remove(user)
            return True
        return False

    def regenerate_join_code(self):
        """Generate a new join code"""
        self.join_code = uuid.uuid4()
        self.save()