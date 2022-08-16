from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_reset/', PasswordResetView.as_view(
            template_name='users/Password_reset_form.html'
        ),
        name='password_reset_form'
    ),
    path(
        'password_reset/done/', PasswordResetDoneView.as_view(
            template_name='users/Password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'password_reset/confirm/', PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'password-change/', views.PasswordChangeView.as_view(
            template_name='users/password_change_form.html'
        ),
        name='password_change_form'
    ),
    path(
        'password-change/done', views.PasswordChangeDone.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done'
    )
]
