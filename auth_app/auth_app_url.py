# auth_app/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views

from auth_app.views.api_key_views import update_api_keys
from auth_app.views.dashboard_views import dashboard_view
from auth_app.views.login_views import login_view
from auth_app.views.logout_views import logout_view
from auth_app.views.sign_up_view import SignUpView
from auth_app.views.profile_views import update_profile, view_profile
from auth_app.forms.custom_password_reset_form import CustomPasswordResetForm
from auth_app.forms.custom_setPassword_form import CustomSetPasswordForm

urlpatterns = [
    # Authentication
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Dashboard
    path('dashboard/', dashboard_view, name='dashboard'),

    # Profile Management
    path('profile/', view_profile, name='profile'),
    path('profile/edit/', update_profile, name='edit_profile'),

    # API Keys
    path('update-keys/', update_api_keys, name='update_api_keys'),

    # Password Reset
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='auth/password_reset.html',
             email_template_name='auth/password_reset_email.html',
             subject_template_name='auth/password_reset_subject.txt',
             form_class=CustomPasswordResetForm
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='auth/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='auth/password_reset_confirm.html',
             form_class=CustomSetPasswordForm
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='auth/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]


# # auth_app/urls.py
#
# from django.urls import path
# from django.contrib.auth import views as auth_views
#
# from auth_app.views.api_key_views import update_api_keys
# from auth_app.views.dashboard_views import dashboard_view
# from auth_app.views.login_views import login_view
# from auth_app.views.logout_views import logout_view
# from auth_app.views.sign_up_view import SignUpView
#
# urlpatterns = [
#     path('signup/', SignUpView.as_view(), name='signup'),
#     path('login/', login_view, name='login'),
#     path('logout/', logout_view, name='logout'),
#     path('dashboard/', dashboard_view, name='dashboard'),
#
#     path('update-keys/', update_api_keys, name='update_api_keys'),
#     path('password-reset/',
#          auth_views.PasswordResetView.as_view(
#              template_name='auth/password_reset.html',
#              email_template_name='auth/password_reset_email.html',
#              subject_template_name='auth/password_reset_subject.txt'
#          ),
#          name='password_reset'),
#     path('password-reset/done/',
#          auth_views.PasswordResetDoneView.as_view(
#              template_name='auth/password_reset_done.html'
#          ),
#          name='password_reset_done'),
#     path('reset/<uidb64>/<token>/',
#          auth_views.PasswordResetConfirmView.as_view(
#              template_name='auth/password_reset_confirm.html'
#          ),
#          name='password_reset_confirm'),
#     path('reset/done/',
#          auth_views.PasswordResetCompleteView.as_view(
#              template_name='auth/password_reset_complete.html'
#          ),
#          name='password_reset_complete'),
# ]
