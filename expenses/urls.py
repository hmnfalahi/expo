from django.urls import path
from .views import group_views, session_views, expense_views, settlement_views
from .views.account_views import send_verification_email

app_name = 'expenses'

urlpatterns = [
    path('', group_views.DashboardView.as_view(), name='dashboard'),
    path('groups/create/', group_views.GroupCreateView.as_view(), name='create_group'),
    path('groups/<int:pk>/', group_views.GroupDetailView.as_view(), name='group_detail'),
    path('groups/<uuid:join_code>/join', group_views.JoinGroupView.as_view(), name='join_group'),
    path('groups/<int:group_id>/remove-member/<int:user_id>/', group_views.RemoveMemberView.as_view(), name='remove_member'),
    path('groups/<int:group_id>/regenerate-join-code/', group_views.RegenerateJoinCodeView.as_view(), name='regenerate_join_code'),
    path('groups/<int:group_id>/leave/', group_views.LeaveGroupView.as_view(), name='leave_group'),
    path('groups/<int:group_id>/update/', group_views.UpdateGroupView.as_view(), name='update_group'),
    path('groups/<int:group_id>/delete/', group_views.DeleteGroupView.as_view(), name='delete_group'),
    path('groups/<int:group_id>/sessions/create/', session_views.SessionCreateView.as_view(), name='create_session'),
    path('sessions/<int:pk>/', session_views.SessionDetailView.as_view(), name='session_detail'),
    path('sessions/<int:pk>/update/', session_views.UpdateSessionView.as_view(), name='update_session'),
    path('sessions/<int:session_id>/add-member/<int:user_id>/', session_views.AddMemberToSessionView.as_view(), name='add_member_to_session'),
    path('sessions/<int:session_id>/remove-member/<int:user_id>/', session_views.RemoveMemberFromSessionView.as_view(), name='remove_member_from_session'),
    path('sessions/<int:session_id>/leave/', session_views.LeaveSessionView.as_view(), name='leave_session'),
    path('sessions/<int:session_id>/delete/', session_views.DeleteSessionView.as_view(), name='delete_session'),
    path('sessions/<int:session_id>/end/', session_views.EndSessionView.as_view(), name='end_session'),
    path('groups/<int:group_id>/sessions/<int:session_id>/add-expense/', expense_views.AddExpenseView.as_view(), name='add_expense'),
    path('expenses/<int:pk>/update/', expense_views.UpdateExpenseView.as_view(), name='update_expense'),
    path('expenses/<int:pk>/', expense_views.ExpenseDetailView.as_view(), name='expense_detail'),
    path('expenses/<int:pk>/delete/', expense_views.DeleteExpenseView.as_view(), name='delete_expense'),
    path('accounts/send-verification/', send_verification_email, name='send_verification'),
    path('settlements/pay/', settlement_views.SubmitPaymentView.as_view(), name='submit_payment'),
    path('settlements/<int:settlement_id>/accept/', settlement_views.AcceptPaymentView.as_view(), name='accept_payment'),
    path('settlements/<int:settlement_id>/details/', settlement_views.PaymentDetailsView.as_view(), name='payment_details'),
]