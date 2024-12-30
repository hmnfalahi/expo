from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse  # Add this import
from ..models import Group, Session, Expense
from ..forms import ExpenseForm


@login_required
def add_expense(request, group_id, session_id):
    group = get_object_or_404(Group, id=group_id)
    session = get_object_or_404(Session, id=session_id)
    
    if session.ended:
        messages.warning(request, 'This session has ended. No further changes can be made.')
        return redirect('expenses:session_detail', session_id=session.id)
    
    if request.user not in group.members.all():
        messages.warning(request, 'You are not a member of this group.')
        return redirect('expenses:dashboard')
    
    if request.user not in session.members.all():
        messages.warning(request, 'You are not a member of this session.')
        return redirect('expenses:session_detail', session_id=session.id)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, session=session)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.group = group
            expense.session = session
            expense.paid_by = request.user
            expense.save()
            form.save_m2m()
            messages.success(request, 'Expense added successfully!')
            return redirect('expenses:session_detail', session_id=session.id)
    else:
        form = ExpenseForm(session=session)
    
    return render(request, 'expenses/add_expense.html', {'form': form, 'group': group, 'session': session})


@login_required
def update_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    session = expense.session
    
    if session.ended:
        messages.error(request, 'This session has ended. No further changes can be made.')
        return redirect('expenses:session_detail', session_id=session.id)
    
    if request.user != expense.paid_by:
        messages.error(request, 'You are not authorized to update this expense.')
        return redirect('expenses:session_detail', session_id=expense.session.id)
    
    group = expense.group  # Get the group from the expense
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense, session=session)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')
            return redirect('expenses:session_detail', session_id=session.id)
    else:
        form = ExpenseForm(instance=expense, session=session)
    return render(request, 'expenses/update_expense.html', {'form': form, 'group': group, 'session': session})

@login_required
def expense_detail(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    return render(request, 'expenses/expense_detail.html', {'expense': expense})

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    session = expense.session
    
    if session.ended:
        return JsonResponse({'success': False, 'error': 'This session has ended. No further changes can be made.'})
    
    if request.user != expense.paid_by:
        return JsonResponse({
            'success': False,
            'error': 'You are not authorized to delete this expense.'
        })
    
    if request.method == 'POST':
        session_id = expense.session.id
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
        return JsonResponse({
            'success': True,
            'redirect_url': reverse('expenses:session_detail', args=[session_id])
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

