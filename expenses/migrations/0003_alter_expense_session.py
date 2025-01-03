# Generated by Django 5.0.1 on 2024-12-22 19:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0002_session_expense_session_group_sessions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='session',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='session_expenses', to='expenses.session'),
            preserve_default=False,
        ),
    ]
