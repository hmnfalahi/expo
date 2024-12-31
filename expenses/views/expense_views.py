from typing import Dict
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from expenses.models import Expense, Session
from expenses.services.expense_service import ExpenseService


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    fields = ['description', 'amount', 'paid_by', 'payment_method', 'date']
    template_name = 'expenses/expense_form.html'

    def form_valid(self, form):
        session = get_object_or_404(Session, pk=self.kwargs['session_id'])
        data = {**form.cleaned_data, 'session': session}

        try:
            expense = ExpenseService.create_expense(session, data)
            return JsonResponse({'status': 'success', 'id': expense.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})


class ExpenseUpdateView(LoginRequiredMixin, UpdateView):
    model = Expense
    fields = ['description', 'amount', 'paid_by', 'payment_method', 'date']
    template_name = 'expenses/expense_form.html'

    def form_valid(self, form):
        expense = form.save(commit=False)
        expense.full_clean()
        expense.save()
        return JsonResponse({'status': 'success'})