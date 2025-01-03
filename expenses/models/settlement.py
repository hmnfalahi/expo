from django.db import models
from django.contrib.auth.models import User
from .session import Session

class Settlement(models.Model):
    session = models.ForeignKey(Session, related_name='settlements', on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, related_name='settlements_from', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='settlements_to', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    document = models.FileField(upload_to='settlements/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted')], default='pending')

    class Meta:
        unique_together = ('session', 'from_user', 'to_user')

    def __str__(self):
        return f'{self.from_user} to {self.to_user} - ${self.amount}'
