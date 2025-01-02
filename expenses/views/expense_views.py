from django.views import View
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from ..models import Group, Session, Expense
from ..forms import ExpenseForm


class AddExpenseView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/add_expense.html'

    def dispatch(self, request, *args, **kwargs):
        self.group = get_object_or_404(Group, id=self.kwargs['group_id'])
        self.session = get_object_or_404(Session, id=self.kwargs['session_id'])
        if self.session.ended:
            messages.warning(request, 'This session has ended. No further changes can be made.')
            return redirect('expenses:session_detail', pk=self.session.id)
        if request.user not in self.group.members.all():
            messages.warning(request, 'You are not a member of this group.')
            return redirect('expenses:dashboard')
        if request.user not in self.session.members.all():
            messages.warning(request, 'You are not a member of this session.')
            return redirect('expenses:session_detail', pk=self.session.id)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        expense = form.save(commit=False)
        expense.group = self.group
        expense.session = self.session
        expense.paid_by = self.request.user
        expense.save()
        form.save_m2m()
        messages.success(self.request, 'Expense added successfully!')
        return redirect('expenses:session_detail', pk=self.session.id)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['session'] = self.session
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        context['session'] = self.session
        return context


class UpdateExpenseView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/update_expense.html'

    def dispatch(self, request, *args, **kwargs):
        self.expense = get_object_or_404(Expense, id=self.kwargs['pk'])
        self.session = self.expense.session
        if self.session.ended:
            messages.error(request, 'This session has ended. No further changes can be made.')
            return redirect('expenses:session_detail', pk=self.session.id)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Expense updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('expenses:session_detail', kwargs={'pk': self.session.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['session'] = self.session
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.expense.group
        context['session'] = self.session
        return context

    def test_func(self):
        return self.request.user == self.expense.paid_by


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    model = Expense
    template_name = 'expenses/expense_detail.html'
    context_object_name = 'expense'


class DeleteExpenseView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, pk):
        expense = get_object_or_404(Expense, id=pk)
        session = expense.session
        if session.ended:
            return JsonResponse({'success': False, 'error': 'This session has ended. No further changes can be made.'})
        if request.user != expense.paid_by:
            return JsonResponse({'success': False, 'error': 'You are not authorized to delete this expense.'})

        try:
            expense.delete()
            messages.success(request, 'Expense deleted successfully!')
            return JsonResponse({'success': True, 'redirect_url': reverse_lazy('expenses:session_detail', kwargs={'pk': session.id})})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    def test_func(self):
        expense = get_object_or_404(Expense, id=self.kwargs['pk'])
        return self.request.user == expense.paid_by

