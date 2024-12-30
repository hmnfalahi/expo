from django.db import models
from django.contrib.auth.models import User


class Session(models.Model):
    group = models.ForeignKey('Group', on_delete=models.CASCADE, related_name='group_sessions')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_sessions')
    members = models.ManyToManyField(User, related_name='session_members')
    ended = models.BooleanField(default=False)

    def __str__(self):
        return self.name
