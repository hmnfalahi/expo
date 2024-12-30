import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from ..models import Group
from ..forms import GroupForm
from ..services.balance_calculator import calculate_balances


@login_required
def dashboard(request):
    user_groups = request.user.expense_groups.all()
    return render(request, 'expenses/dashboard.html', {'groups': user_groups})


@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create the group
                    group = form.save(commit=False)
                    group.created_by = request.user
                    group.save()
                    
                    # Add the creator as a member
                    group.members.add(request.user)
                    
                    messages.success(request, 'Group created successfully!')
                    return redirect('expenses:group_detail', group_id=group.id)
            except Exception as e:
                messages.error(request, f'Error creating group: {str(e)}')
                return redirect('expenses:dashboard')
    else:
        form = GroupForm()
    
    return render(request, 'expenses/create_group.html', {
        'form': form,
        'title': 'Create New Group'
    })


@login_required
def group_detail(request, group_id):
    """
    Display group details, sessions, and balances.
    Only accessible to group members.
    """
    group = get_object_or_404(Group, id=group_id)
    
    # Check if user is a member of the group
    if request.user not in group.members.all():
        messages.warning(request, 'You are not a member of this group.')  # Changed from error to warning
        return redirect('expenses:dashboard')
    
    # Get all sessions for the group, ordered by ended status and date
    sessions = group.group_sessions.all().order_by('ended', '-created_at')
    expenses = group.expenses.all()  # Corrected this line
    
    # Calculate current balances
    balances = calculate_balances(group)
    
    context = {
        'group': group,
        'sessions': sessions,
        'expenses': expenses,  # Corrected this line
        'balances': balances,
        'title': f'Group: {group.name}',
        'is_creator': request.user == group.created_by,
        'join_url': request.build_absolute_uri(f'/join/{group.join_code}/')
    }
    
    return render(request, 'expenses/group_detail.html', context)


@login_required
def join_group(request, join_code):
    """Join a group using the join code"""
    try:
        group = Group.objects.get(join_code=join_code)
        if request.user not in group.members.all():
            group.members.add(request.user)
            messages.success(request, f'You have joined the group: {group.name}')
        else:
            messages.info(request, 'You are already a member of this group')
        return redirect('expenses:group_detail', group_id=group.id)
    except Group.DoesNotExist:
        messages.error(request, 'Invalid join link')
        return redirect('expenses:dashboard')


@login_required
def remove_member(request, group_id, user_id):
    """Remove a member from the group and all its sessions"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    group = get_object_or_404(Group, id=group_id)
    if request.user != group.created_by:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        user_to_remove = User.objects.get(id=user_id)
        # Check if user has non-zero balance in the group
        balances = calculate_balances(group)
        if balances.get(user_to_remove, 0) != 0:
            return JsonResponse({'error': 'Cannot remove member with non-zero balance'}, status=400)

        # First check balances in all sessions
        for session in group.group_sessions.all():
            session_balances = calculate_balances(session)
            if session_balances.get(user_to_remove, 0) != 0:
                return JsonResponse({'error': 'Cannot remove member with non-zero balance in session: ' + session.name}, status=400)

        # If all balances are zero, proceed with removal
        with transaction.atomic():
            # Remove from all sessions first
            for session in group.group_sessions.all():
                session.members.remove(user_to_remove)
            
            # Then remove from group
            if group.remove_member(user_to_remove):
                messages.success(request, f'{user_to_remove.username} has been removed from the group and all its sessions')
            else:
                messages.error(request, 'Cannot remove the group creator')
            return JsonResponse({'success': True})

    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)


@login_required
def regenerate_join_code(request, group_id):
    """Generate a new join code for the group"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    group = get_object_or_404(Group, id=group_id)
    if request.user != group.created_by:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    group.regenerate_join_code()
    return JsonResponse({
        'success': True,
        'new_join_url': request.build_absolute_uri(f'/join/{group.join_code}/')
    })


@login_required
def leave_group(request, group_id):
    """Allow a member to leave a group if their balance is zero"""
    group = get_object_or_404(Group, id=group_id)

    if request.user not in group.members.all():
        return JsonResponse({'error': 'You are not a member of this group'}, status=403)

    balances = calculate_balances(group)
    if balances.get(request.user, 0) != 0:
        return JsonResponse({'error': 'Cannot leave group with non-zero balance'}, status=400)

    group.members.remove(request.user)
    messages.success(request, 'You have left the group')
    return JsonResponse({'success': True})


@login_required
@require_POST
@csrf_exempt
def update_group(request, group_id):
    """Update group name and description"""
    group = get_object_or_404(Group, id=group_id)
    if request.user != group.created_by:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    data = json.loads(request.body)
    group.name = data.get('name', group.name)
    group.description = data.get('description', group.description)
    group.save()

    return JsonResponse({'success': True})


@login_required
def delete_group(request, group_id):
    """Delete a group"""
    group = get_object_or_404(Group, id=group_id)
    
    # Check if user is the group creator
    if request.user != group.created_by:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        group.delete()
        messages.success(request, 'Group deleted successfully')
        return JsonResponse({'success': True, 'redirect_url': f'/'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

