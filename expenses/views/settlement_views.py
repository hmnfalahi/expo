from django.views import View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.files.storage import default_storage
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from ..models import Settlement

@method_decorator(csrf_exempt, name='dispatch')
class SubmitPaymentView(View):
    def post(self, request):
        from_user_id = request.POST.get('from_user')
        to_user_id = request.POST.get('to_user')
        amount = request.POST.get('amount')

        from_user = get_object_or_404(User, id=from_user_id)
        to_user = get_object_or_404(User, id=to_user_id)

        document = request.FILES.get('document')
        if not document:
            return JsonResponse({'error': 'No document uploaded'}, status=400)

        file_path = default_storage.save(f'settlements/{from_user_id}_{to_user_id}/{document.name}', document)

        settlement = Settlement.objects.create(
            from_user=from_user,
            to_user=to_user,
            amount=amount,
            document=file_path,
            status='pending'
        )

        messages.success(request, 'Payment submitted successfully')
        return JsonResponse({'success': True})

class AcceptPaymentView(View):
    def post(self, request, settlement_id):
        settlement = get_object_or_404(Settlement, id=settlement_id)
        if settlement.status != 'pending':
            return JsonResponse({'error': 'No pending payment to accept'}, status=400)

        settlement.status = 'accepted'
        settlement.save()

        messages.success(request, 'Payment accepted successfully')
        return JsonResponse({'success': True})

class PaymentDetailsView(View):
    def get(self, request, settlement_id):
        settlement = get_object_or_404(Settlement, id=settlement_id)
        data = {
            'exists': True,
            'from_user': settlement.from_user.username,
            'to_user': settlement.to_user.username,
            'to_user_id': settlement.to_user.id,
            'amount': settlement.amount,
            'status': settlement.get_status_display(),
            'document': settlement.document.url if settlement.document else None
        }
        return JsonResponse(data)
