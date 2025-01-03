from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/manage/', TemplateView.as_view(template_name='account/manage.html'), name='account_manage'),
    path('accounts/email/', RedirectView.as_view(pattern_name='account_manage', permanent=True), name='account_email'),
    path('accounts/', include('allauth.urls')),
    path('', include('expenses.urls')),
]