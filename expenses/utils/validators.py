from decimal import Decimal
from django.core.exceptions import ValidationError

def validate_positive_amount(value):
    if not isinstance(value, (int, float, Decimal)) or value <= 0:
        raise ValidationError("Amount must be a positive number")

def validate_group_member_limit(group):
    if group.members.count() > 20:
        raise ValidationError("A group cannot have more than 20 members")