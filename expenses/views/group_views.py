import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.decorators import method_decorator

from ..models import Group
from ..forms import GroupForm
from ..services.balance_calculator import calculate_balances


class DashboardView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'expenses/dashboard.html'
    context_object_name = 'groups'

    def get_queryset(self):
        return self.request.user.expense_groups.all()


class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'expenses/create_group.html'

    def form_valid(self, form):
        try:
            with transaction.atomic():
                group = form.save(commit=False)
                group.created_by = self.request.user
                group.save()
                group.members.add(self.request.user)
                messages.success(self.request, 'Group created successfully!')
                return redirect('expenses:group_detail', pk=group.pk)
        except Exception as e:
            messages.error(self.request, f'Error creating group: {str(e)}')
            return redirect('expenses:dashboard')


class GroupDetailView(LoginRequiredMixin, DetailView):
    model = Group
    template_name = 'expenses/group_detail.html'
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        if self.request.user not in group.members.all():
            messages.warning(self.request, 'You are not a member of this group.')
            return redirect('expenses:dashboard')
        context['sessions'] = group.group_sessions.all().order_by('ended', '-created_at')
        context['expenses'] = group.expenses.all()
        context['balances'] = calculate_balances(group)
        context['is_creator'] = self.request.user == group.created_by
        context['join_url'] = self.request.build_absolute_uri(f'/groups/{group.join_code}/join')
        return context


class JoinGroupView(LoginRequiredMixin, View):
    def get(self, request, join_code):
        try:
            group = Group.objects.get(join_code=join_code)
            if request.user not in group.members.all():
                group.members.add(request.user)
                messages.success(request, f'You have joined the group: {group.name}')
            else:
                messages.info(request, 'You are already a member of this group')
            return redirect('expenses:group_detail', pk=group.pk)
        except Group.DoesNotExist:
            messages.error(request, 'Invalid join link')
            return redirect('expenses:dashboard')


class RemoveMemberView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, group_id, user_id):
        group = get_object_or_404(Group, id=group_id)
        if not self.test_func():
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        try:
            user_to_remove = User.objects.get(id=user_id)
            balances = calculate_balances(group)
            if balances.get(user_to_remove, 0) != 0:
                return JsonResponse({'error': 'Cannot remove member with non-zero balance'}, status=400)

            for session in group.group_sessions.all():
                session_balances = calculate_balances(session)
                if session_balances.get(user_to_remove, 0) != 0:
                    return JsonResponse({'error': f'Cannot remove member with non-zero balance in session: {session.name}'}, status=400)

            with transaction.atomic():
                for session in group.group_sessions.all():
                    session.members.remove(user_to_remove)
                if group.remove_member(user_to_remove):
                    messages.success(request, f'{user_to_remove.username} has been removed from the group and all its sessions')
                else:
                    messages.error(request, 'Cannot remove the group creator')
                return JsonResponse({'success': True})

        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

    def test_func(self):
        group = get_object_or_404(Group, id=self.kwargs['group_id'])
        return self.request.user == group.created_by


class RegenerateJoinCodeView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        if not self.test_func():
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        group.regenerate_join_code()
        return JsonResponse({
            'success': True,
            'new_join_url': request.build_absolute_uri(f'/join/{group.join_code}/')
        })

    def test_func(self):
        group = get_object_or_404(Group, id=self.kwargs['group_id'])
        return self.request.user == group.created_by


class LeaveGroupView(LoginRequiredMixin, View):
    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        if request.user not in group.members.all():
            return JsonResponse({'error': 'You are not a member of this group'}, status=403)

        balances = calculate_balances(group)
        if balances.get(request.user, 0) != 0:
            return JsonResponse({'error': 'Cannot leave group with non-zero balance'}, status=400)

        group.members.remove(request.user)
        messages.success(request, 'You have left the group')
        return JsonResponse({'success': True})


@method_decorator(csrf_exempt, name='dispatch')
class UpdateGroupView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        if not self.test_func():
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        data = json.loads(request.body)
        group.name = data.get('name', group.name)
        group.description = data.get('description', group.description)
        group.save()

        return JsonResponse({'success': True})

    def test_func(self):
        group = get_object_or_404(Group, id=self.kwargs['group_id'])
        return self.request.user == group.created_by


class DeleteGroupView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        if not self.test_func():
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        try:
            group.delete()
            messages.success(request, 'Group deleted successfully')
            return JsonResponse({'success': True, 'redirect_url': reverse_lazy('expenses:dashboard')})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def test_func(self):
        group = get_object_or_404(Group, id=self.kwargs['group_id'])
        return self.request.user == group.created_by

