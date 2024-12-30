from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from expenses.views import auth_views as custom_auth_views


def trigger_error(request):
    division_by_zero = 1 / 0


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('expenses.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', custom_auth_views.register, name='register'),
    path('sentry-debug/', trigger_error),
]