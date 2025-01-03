from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from django.contrib.auth import login
from django.contrib.auth import get_user_model

@require_POST
@login_required
def send_verification_email(request):
    email_address = EmailAddress.objects.get_or_create(
        user=request.user,
        email=request.user.email
    )[0]
    
    if not email_address.verified:
        send_email_confirmation(request, request.user)
        # Specify the authentication backend explicitly
        if not hasattr(request.user, 'backend'):
            request.user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, request.user)
        
        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f'Verification email sent'
            })
        return redirect('account_email_verification_sent')
    
    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'info',
            'message': 'Email is already verified'
        })
    messages.info(request, 'Email is already verified')
    return redirect('account_manage')
