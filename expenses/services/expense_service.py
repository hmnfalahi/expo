from typing import List, Dict
from decimal import Decimal
from django.db import transaction
from expenses.models import Expense, Session
from expenses.utils.calculations import calculate_member_balances


class ExpenseService:
    @staticmethod
    @transaction.atomic
    def create_expense(session: Session, data: Dict) -> Expense:
        expense = Expense(
            session=session,
            description=data['description'],
            amount=data['amount'],
            paid_by=data['paid_by'],
            payment_method=data.get('payment_method', 'CASH'),
            date=data['date']
        )
        expense.full_clean()
        expense.save()
        return expense

    @staticmethod
    def get_session_summary(session: Session) -> Dict:
        expenses = session.expenses.all()
        members = session.group.members.all()

        return {
            'total_amount': sum(e.amount for e in expenses),
            'member_count': len(members),
            'balances': calculate_member_balances(expenses, members)
        }