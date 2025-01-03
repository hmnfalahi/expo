from django.db import migrations
from django.conf import settings

def create_social_app(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    
    site = Site.objects.get(id=settings.SITE_ID)
    
    google_app = SocialApp.objects.create(
        provider='google',
        name='Google OAuth',
        client_id=getattr(settings, 'GOOGLE_CLIENT_ID', ''),
        secret=getattr(settings, 'GOOGLE_SECRET_KEY', '')
    )
    google_app.sites.add(site)

def remove_social_app(apps, schema_editor):
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    SocialApp.objects.filter(provider='google').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('expenses', '0002_create_default_site'),
        ('sites', '0002_alter_domain_unique'),
        ('socialaccount', '0003_extra_data_default_dict'),
    ]

    operations = [
        migrations.RunPython(create_social_app, remove_social_app)
    ]
