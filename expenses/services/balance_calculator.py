from collections import defaultdict
from typing import Dict, Union
from decimal import Decimal
from django.contrib.auth.models import User
from django.utils.dateparse import parse_datetime
from ..models import Group, Session

def calculate_balances(obj):
    """Calculate balances for a group or session"""
    balances = {}
    
    # Get expenses based on whether this is a group or session
    expenses = obj.expenses.all() if hasattr(obj, 'expenses') else obj.session_expenses.all()
    
    # Initialize balances for all members to 0
    members = obj.members.all()
    for member in members:
        balances[member] = Decimal('0.00')

    # Calculate balances
    for expense in expenses:
        # Get the amount per person
        split_count = expense.split_with.count()
        if split_count > 0:
            amount_per_person = expense.amount / split_count
            
            # Add the full amount to the payer's balance
            balances[expense.paid_by] = balances.get(expense.paid_by, Decimal('0.00')) + expense.amount
            
            # Subtract each person's share from their balance
            for user in expense.split_with.all():
                balances[user] = balances.get(user, Decimal('0.00')) - amount_per_person

    return balances

def calculate_settlements(balances):
    """Calculate the optimal way to settle debts"""
    settlements = []
    # Convert balances dict to list of (user, amount) tuples
    balance_list = [(user, float(amount)) for user, amount in balances.items()]
    
    # Sort by balance amount
    debtors = sorted([b for b in balance_list if b[1] < 0], key=lambda x: x[1])
    creditors = sorted([b for b in balance_list if b[1] > 0], key=lambda x: x[1], reverse=True)
    
    i, j = 0, 0
    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]
        
        amount = min(abs(debtor[1]), creditor[1])
        if amount > 0.01:  # Ignore very small amounts
            settlements.append({
                'from_user': debtor[0],
                'to_user': creditor[0],
                'amount': round(amount, 2)
            })
        
        # Update balances and move to next person if settled
        debtors[i] = (debtor[0], debtor[1] + amount)
        creditors[j] = (creditor[0], creditor[1] - amount)
        
        if abs(debtors[i][1]) < 0.01:
            i += 1
        if abs(creditors[j][1]) < 0.01:
            j += 1
            
    return settlements