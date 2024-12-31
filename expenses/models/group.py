from django.db import models
from django.conf import settings
from expenses.utils.validators import validate_group_member_limit


class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_groups'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='expense_groups'
    )

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        validate_group_member_limit(self)

    def add_member(self, user):
        if not self.members.filter(id=user.id).exists():
            self.members.add(user)

    def get_total_expenses(self):
        return sum(session.total_amount for session in self.sessions.all())