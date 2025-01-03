from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from allauth.account.utils import user_email

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Try to get existing user by email
        user = sociallogin.user
        if user.id or not user.email:
            return

        try:
            user = get_user_model().objects.get(email=user.email)
            sociallogin.connect(request, user)
        except get_user_model().DoesNotExist:
            pass

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if not user.username:
            # Set username from email if not provided
            user.username = user.email.split('@')[0]
        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        return user

class CustomAccountAdapter(DefaultAccountAdapter):
    def pre_login(self, request, user, **kwargs):
        # Keep user logged in during verification process
        if not user.is_active:
            return
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return super().pre_login(request, user, **kwargs)

    def get_login_redirect_url(self, request):
        # Check if email verification is required
        if not request.user.emailaddress_set.filter(verified=True).exists():
            return '/accounts/confirm-email/'
        return super().get_login_redirect_url(request)

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        # Keep user logged in when sending confirmation email
        if request.user.is_anonymous and emailconfirmation.email_address.user:
            login(request, emailconfirmation.email_address.user, 
                  backend='django.contrib.auth.backends.ModelBackend')
        return super().send_confirmation_mail(request, emailconfirmation, signup)
