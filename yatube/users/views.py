from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:home_page')
    template_name = 'users/signup.html'


class Login(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:home_page')
    template_name = 'users/login.html'


class PasswordResetView(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('users:password_reset_done')
    template_name = 'users/password_reset_form.html'


class PasswordResetDoneView(CreateView):
    form_class = CreationForm
    template_name = 'users/password_reset_done.html'


class PasswordChangeView(CreateView):
    form_class = CreationForm
    template_name = 'users/password_change_form.html'
    success_url = reverse_lazy('users:password_change_done')


class PasswordChangeDone(CreateView):
    form_class = CreationForm
    template_name = 'users/password_change_done.html'
