from django.contrib import admin
from .models import Group, Expense


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
    search_fields = ('name', 'created_by__username')
    filter_horizontal = ('members',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'paid_by', 'group', 'date')
    list_filter = ('group', 'date', 'paid_by')
    search_fields = ('description', 'paid_by__username')
    filter_horizontal = ('split_with',)