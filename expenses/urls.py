from django.urls import path
from .views import group_views, session_views, expense_views


app_name = 'expenses'

urlpatterns = [
    path('', group_views.dashboard, name='dashboard'),
    path('groups/create/', group_views.create_group, name='create_group'),
    path('groups/<int:group_id>/', group_views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/sessions/<int:session_id>/add-expense/', expense_views.ExpenseCreateView.as_view, name='add_expense'),
    path('groups/<uuid:join_code>/join', group_views.join_group, name='join_group'),
    path('groups/<int:group_id>/remove-member/<int:user_id>/', group_views.remove_member, name='remove_member'),
    path('groups/<int:group_id>/regenerate-join-code/', group_views.regenerate_join_code, name='regenerate_join_code'),
    path('groups/<int:group_id>/leave/', group_views.leave_group, name='leave_group'),
    path('groups/<int:group_id>/update/', group_views.update_group, name='update_group'),
    path('groups/<int:group_id>/delete/', group_views.delete_group, name='delete_group'),
    path('expenses/<int:expense_id>/update/', expense_views.ExpenseUpdateView.as_view, name='update_expense'),
    path('expenses/<int:expense_id>/', expense_views.expense_detail, name='expense_detail'),
    path('expenses/<int:expense_id>/delete/', expense_views.delete_expense, name='delete_expense'),
    path('groups/<int:group_id>/sessions/create/', session_views.create_session, name='create_session'),
    path('sessions/<int:session_id>/', session_views.session_detail, name='session_detail'),
    path('sessions/<int:session_id>/update/', session_views.update_session, name='update_session'),
    path('sessions/<int:session_id>/add-member/<int:user_id>/', session_views.add_member_to_session, name='add_member_to_session'),
    path('sessions/<int:session_id>/remove-member/<int:user_id>/', session_views.remove_member_from_session, name='remove_member_from_session'),
    path('sessions/<int:session_id>/leave/', session_views.leave_session, name='leave_session'),
    path('sessions/<int:session_id>/delete/', session_views.delete_session, name='delete_session'),
    path('sessions/<int:session_id>/end/', session_views.end_session, name='end_session'),
]