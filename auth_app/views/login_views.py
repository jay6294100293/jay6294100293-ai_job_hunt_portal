# from django.contrib import messages
# from django.contrib.auth import login
# from django.shortcuts import render, redirect
#
# from auth_app.forms.custom_authentication_form import CustomAuthenticationForm
#
#
# def login_view(request):
#     if request.method == 'POST':
#         form = CustomAuthenticationForm(data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             messages.success(request, 'Login successful!')
#             return redirect('dashboard')
#     else:
#         form = CustomAuthenticationForm()
#     return render(request, 'auth/login.html', {'form': form})

# auth_app/views/login_views.py

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

# Assuming CustomAuthenticationForm is correctly defined and imported
from auth_app.forms.custom_authentication_form import CustomAuthenticationForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard') # Redirect if already logged in

    if request.method == 'POST':
        # Pass request to AuthenticationForm, it needs it.
        form = CustomAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Login successful! Welcome back, {user.username}.')
            # Redirect to dashboard or 'next' page if provided (e.g., from @login_required)
            next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            # The form itself will contain more specific errors if field validation fails.
            # This is a general message if form.is_valid() is false due to authentication failure.
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = CustomAuthenticationForm(request=request) # Pass request here too for initial form

    # Ensure 'auth/login.html' is the correct path to your template.
    return render(request, 'auth/login.html', {'form': form})