from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.models import User
from ..models import Group, Session  # Ensure correct import
from ..forms import SessionForm
from ..services.balance_calculator import calculate_balances

@login_required
def create_session(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user not in group.members.all():
        messages.error(request, 'You are not a member of this group.')
        return redirect('expenses:group_detail', group_id=group.id)

    if request.method == 'POST':
        form = SessionForm(request.POST, group=group, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    session = form.save(commit=False)
                    session.group = group
                    session.created_by = request.user
                    session.save()
                    form.save_m2m()
                    messages.success(request, 'Session created successfully!')
                    return redirect('expenses:group_detail', group_id=group.id)
            except Exception as e:
                messages.error(request, f'Error creating session: {str(e)}')
                return redirect('expenses:group_detail', group_id=group.id)
    else:
        form = SessionForm(group=group, user=request.user)

    return render(request, 'expenses/create_session.html', {
        'form': form,
        'group': group,
        'title': 'Create New Session'
    })

@login_required
def session_detail(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    group = session.group

    # Check if user is a member of the group
    if request.user not in group.members.all():
        messages.error(request, 'You are not a member of this group.')
        return redirect('expenses:dashboard')

    # Get all expenses for the session, ordered by date
    expenses = session.session_expenses.all().order_by('-date')

    # Calculate current balances for the session
    balances = calculate_balances(session)

    context = {
        'session': session,
        'group': group,
        'expenses': expenses,
        'balances': balances,
        'title': f'Session: {session.name}',
        'is_creator': request.user == session.created_by,
    }

    return render(request, 'expenses/session_detail.html', context)

@login_required
def add_member_to_session(request, session_id, user_id):
    """Add a member to a session"""
    session = get_object_or_404(Session, id=session_id)
    if session.ended:
        return JsonResponse({'error': 'This session has ended. No further changes can be made.'}, status=400)
    group = session.group
    if request.user != group.created_by and request.user != session.created_by:
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


@login_required
def remove_member_from_session(request, session_id, user_id):
    """Remove a member from a session"""
    session = get_object_or_404(Session, id=session_id)
    if session.ended:
        return JsonResponse({'error': 'This session has ended. No further changes can be made.'}, status=400)
    group = session.group
    if request.user != group.created_by and request.user != session.created_by:
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

@login_required
def leave_session(request, session_id):
    """Allow a member to leave a session if their balance is zero"""
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

@login_required
def delete_session(request, session_id):
    """Delete a session"""
    session = get_object_or_404(Session, id=session_id)
    if session.ended:
        return JsonResponse({'error': 'This session has ended. No further changes can be made.'}, status=400)
    group = session.group
    
    # Check if user is authorized (group creator or session creator)
    if request.user != group.created_by and request.user != session.created_by:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        session.delete()
        messages.success(request, 'Session deleted successfully')
        return JsonResponse({'success': True, 'redirect_url': f'/group/{group.id}/'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def update_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if session.ended:
        messages.warning(request, 'This session has ended. No further changes can be made.')
        return redirect('expenses:session_detail', session_id=session.id)
    group = session.group

    if request.user != session.created_by and request.user != group.created_by:
        messages.error(request, 'You are not authorized to update this session.')
        return redirect('expenses:session_detail', session_id=session.id)

    balances = calculate_balances(session)

    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session, group=group, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Session updated successfully!')
            return redirect('expenses:session_detail', session_id=session.id)
    else:
        form = SessionForm(instance=session, group=group, user=request.user)

    return render(request, 'expenses/update_session.html', {
        'form': form,
        'session': session,
        'title': 'Update Session',
        'balances': balances
    })

@login_required
def end_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    group = session.group

    if request.user != session.created_by and request.user != group.created_by:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    session.ended = True
    session.save()
    messages.success(request, 'Session ended successfully')
    return JsonResponse({'success': True})
