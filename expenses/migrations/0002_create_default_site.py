from django.db import migrations
from django.contrib.sites.models import Site

def create_default_site(apps, schema_editor):
    Site.objects.get_or_create(
        pk=1,
        defaults={
            'domain': 'localhost:8000',
            'name': 'Expense Tracker'
        }
    )

def remove_default_site(apps, schema_editor):
    Site.objects.filter(pk=1).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('expenses', '0001_initial'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(create_default_site, remove_default_site)
    ]
