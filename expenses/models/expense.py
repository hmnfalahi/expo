from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Expense(models.Model):
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    session = models.ForeignKey(
        'Session',
        on_delete=models.CASCADE,
        related_name='session_expenses'
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='paid_expenses'
    )
    split_with = models.ManyToManyField(
        User,
        related_name='split_expenses'
    )
    date = models.DateField(default=timezone.now)  # Changed from DateTimeField to DateField
    created_at = models.DateTimeField(auto_now_add=True)  # Add this field

    def save(self, *args, **kwargs):
        if isinstance(self.date, str):
            self.date = timezone.datetime.strptime(self.date, '%Y-%m-%d').date()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.description