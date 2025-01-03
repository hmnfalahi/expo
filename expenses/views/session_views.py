from django.views import View
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User  # Add this import

from ..models import Group, Session
from ..forms import SessionForm
from ..services.balance_calculator import calculate_balances
from ..mixins import EmailVerificationRequiredMixin


class SessionCreateView(EmailVerificationRequiredMixin, LoginRequiredMixin, CreateView):
    model = Session
    form_class = SessionForm
    template_name = 'expenses/create_session.html'

    def dispatch(self, request, *args, **kwargs):
        self.group = get_object_or_404(Group, id=self.kwargs['group_id'])
        if request.user not in self.group.members.all():
            messages.error(request, 'You are not a member of this group.')
            return redirect('expenses:group_detail', pk=self.group.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            with transaction.atomic():
                session = form.save(commit=False)
                session.group = self.group
                session.created_by = self.request.user
                session.save()
                form.save_m2m()
                messages.success(self.request, 'Session created successfully!')
                return redirect('expenses:session_detail', pk=session.pk)
        except Exception as e:
            messages.error(self.request, f'Error creating session: {str(e)}')
            return redirect('expenses:group_detail', pk=self.group.pk)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['group'] = self.group
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        context['title'] = 'Create New Session'
        return context


class SessionDetailView(EmailVerificationRequiredMixin, LoginRequiredMixin, DetailView):
    model = Session
    template_name = 'expenses/session_detail.html'
    context_object_name = 'session'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_object()
        group = session.group
        if self.request.user not in group.members.all():
            messages.error(self.request, 'You are not a member of this group.')
            return redirect('expenses:dashboard')
        context['group'] = group
        context['expenses'] = session.session_expenses.all().order_by('-date')
        context['balances'] = calculate_balances(session)
        context['is_creator'] = self.request.user == session.created_by
        return context


class AddMemberToSessionView(EmailVerificationRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, session_id, user_id):
        session = get_object_or_404(Session, id=session_id)
        if session.ended:
            return JsonResponse({'error': 'Cannot modify an ended session.'}, status=403)
        group = session.group
        if not self.test_func():
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        try:
            user_to_add = User.objects.get(id=user_id)
            if user_to_add in group.members.all():
                session.members.add(user_to_add)
                messages.success(request, f'{user_to_add.username} has been added to the session')
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'User is not a member of the group'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

    def test_func(self):
        session = get_object_or_404(Session, id=self.kwargs['session_id'])
        group = session.group
        return self.request.user == group.created_by or self.request.user == session.created_by


class RemoveMemberFromSessionView(EmailVerificationRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, session_id, user_id):
        session = get_object_or_404(Session, id=session_id)
        if session.ended:
            return JsonResponse({'error': 'Cannot modify an ended session.'}, status=403)
        group = session.group
        if not self.test_func():
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        try:
            user_to_remove = User.objects.get(id=user_id)
            if user_to_remove in session.members.all():
                balances = calculate_balances(session)
                if balances.get(user_to_remove, 0) != 0:
                    return JsonResponse({'error': 'Cannot remove member with non-zero balance'}, status=400)
                session.members.remove(user_to_remove)
                messages.success(request, f'{user_to_remove.username} has been removed from the session')
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'User is not a member of the session'}, status=400)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

    def test_func(self):
        session = get_object_or_404(Session, id=self.kwargs['session_id'])
        group = session.group
        return self.request.user == group.created_by or self.request.user == session.created_by


class LeaveSessionView(EmailVerificationRequiredMixin, LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(Session, id=session_id)
        if session.ended:
            return JsonResponse({'error': 'This session has ended. No further changes can be made.'}, status=400)
        group = session.group

        if request.user not in session.members.all():
            return JsonResponse({'error': 'You are not a member of this session'}, status=403)

        balances = calculate_balances(session)
        if balances.get(request.user, 0) != 0:
            return JsonResponse({'error': 'Cannot leave session with non-zero balance'}, status=400)

        session.members.remove(request.user)
        messages.success(request, 'You have left the session')
        return JsonResponse({'success': True})


class DeleteSessionView(EmailVerificationRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(Session, id=session_id)
        if session.ended:
            return JsonResponse({'error': 'Cannot delete an ended session.'}, status=403)
        group = session.group
        if not self.test_func():
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        try:
            session.delete()
            messages.success(request, 'Session deleted successfully')
            return JsonResponse({'success': True, 'redirect_url': reverse_lazy('expenses:group_detail', kwargs={'pk': group.id})})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def test_func(self):
        session = get_object_or_404(Session, id=self.kwargs['session_id'])
        group = session.group
        return self.request.user == group.created_by or self.request.user == session.created_by


class UpdateSessionView(EmailVerificationRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Session
    form_class = SessionForm
    template_name = 'expenses/update_session.html'

    def dispatch(self, request, *args, **kwargs):
        self.session = get_object_or_404(Session, id=self.kwargs['pk'])
        if self.session.ended:
            messages.error(request, 'Cannot modify an ended session.')
            return redirect('expenses:session_detail', pk=self.session.id)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Session updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('expenses:session_detail', kwargs={'pk': self.session.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['group'] = self.session.group
        kwargs['user'] = self.request.user
        return kwargs

    def test_func(self):
        group = self.session.group
        return self.request.user == group.created_by or self.request.user == self.session.created_by


class EndSessionView(EmailVerificationRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(Session, id=session_id)
        group = session.group
        if not self.test_func():
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        session.ended = True
        session.save()
        messages.success(request, 'Session ended successfully')
        return JsonResponse({'success': True})

    def test_func(self):
        session = get_object_or_404(Session, id=self.kwargs['session_id'])
        group = session.group
        return self.request.user == group.created_by or self.request.user == session.created_by
