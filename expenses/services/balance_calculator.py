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