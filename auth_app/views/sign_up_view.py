# auth_app/views/sign_up_view.py

from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from auth_app.forms.custom_user_creation_form import CustomUserCreationForm


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')  # Redirect to login page after successful signup
    template_name = 'auth/signup.html'  # Ensure this template exists

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')  # Redirect if already logged in
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # The user is saved by super().form_valid(form) by default.
        response = super().form_valid(form)
        messages.success(self.request, _('Account created successfully! Please log in.'))
        return response

    def form_invalid(self, form):
        # It's good practice to inform the user that there were errors.
        # The form itself will render field-specific errors in the template.
        messages.error(self.request, _("There was an error with your registration. Please check the details provided below."))
        return super().form_invalid(form)

# # auth_app/views.py
#
# from django.shortcuts import render, redirect
# from django.contrib.auth import login, logout
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.views.generic import CreateView
# from django.urls import reverse_lazy
#
# from auth_app.forms.custom_user_creation_form import CustomUserCreationForm
#
#
# class SignUpView(CreateView):
#     form_class = CustomUserCreationForm
#     success_url = reverse_lazy('login')
#     template_name = 'auth/signup.html'
#
#     def form_valid(self, form):
#         response = super().form_valid(form)
#         messages.success(self.request, 'Account created successfully! Please log in.')
#         return response
#
#
#
#


# auth_app/views/sign_up_view.py
