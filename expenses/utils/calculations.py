from decimal import Decimal
from typing import Dict, List


def calculate_split_amount(total: Decimal, num_members: int) -> Decimal:
    return total / Decimal(num_members)


def calculate_member_balances(expenses: List, members: List) -> Dict:
    balances = {member.id: Decimal('0.00') for member in members}

    for expense in expenses:
        paid_by = expense.paid_by_id
        amount = expense.amount
        split = amount / len(members)

        balances[paid_by] += amount
        for member in members:
            balances[member.id] -= split

    return balances