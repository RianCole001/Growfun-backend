from django.urls import path
from .views import (
    RegisterView, LoginView, VerifyEmailView, ResendVerificationEmailView,
    ForgotPasswordView, ResetPasswordView,
    CurrentUserView, UserProfileView, UserSettingsView,
    ChangePasswordView, UserBalanceView, AdminUsersListView,
    AdminUserDetailView, AdminUserVerifyView, AdminUserSuspendView,
    AdminUserResetPasswordView, UserReferralsView, ReferralStatsView,
    generate_referral_code, dashboard_stats, admin_suspended_users,
    admin_user_stats, create_test_notification, admin_dashboard_overview
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    
    # User
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('settings/', UserSettingsView.as_view(), name='settings'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('balance/', UserBalanceView.as_view(), name='balance'),
    path('dashboard-stats/', dashboard_stats, name='dashboard-stats'),
    
    # Referrals
    path('referrals/', UserReferralsView.as_view(), name='referrals'),
    path('referral-stats/', ReferralStatsView.as_view(), name='referral-stats'),
    path('generate-referral-code/', generate_referral_code, name='generate-referral-code'),
    
    # Testing
    path('create-test-notification/', create_test_notification, name='create-test-notification'),
    
    # Admin
    path('admin/dashboard/', admin_dashboard_overview, name='admin-dashboard'),
    path('admin/users/', AdminUsersListView.as_view(), name='admin-users-list'),
    path('admin/users/suspended/', admin_suspended_users, name='admin-suspended-users'),
    path('admin/users/stats/', admin_user_stats, name='admin-user-stats'),
    path('admin/users/<int:user_id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/users/<int:user_id>/verify/', AdminUserVerifyView.as_view(), name='admin-user-verify'),
    path('admin/users/<int:user_id>/suspend/', AdminUserSuspendView.as_view(), name='admin-user-suspend'),
    path('admin/users/<int:user_id>/reset-password/', AdminUserResetPasswordView.as_view(), name='admin-user-reset-password'),
]
