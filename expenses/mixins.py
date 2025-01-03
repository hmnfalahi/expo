from django.shortcuts import redirect
from django.contrib import messages


class EmailVerificationRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        if not request.user.emailaddress_set.filter(verified=True).exists():
            messages.warning(request, 'Please verify your email address first.')
            return redirect('account_email_verification_sent')
        return super().dispatch(request, *args, **kwargs)
