from django import template


register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def amount_per_member(amount, split_count):
    if split_count > 0:
        return amount / split_count
    return 0

@register.filter
def count_expenses_by_member(expenses, member):
    return expenses.filter(paid_by=member).count()

@register.filter
def count_sessions_by_member(sessions, member):
    return sessions.filter(members=member).count()

@register.filter
def count_group_expenses_by_member(group_expenses, member):
    return group_expenses.filter(paid_by=member).count()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
