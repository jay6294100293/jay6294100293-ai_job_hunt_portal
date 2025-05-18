# from django.contrib import messages
# from django.contrib.auth import logout
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import redirect
#
#
# @login_required
# def logout_view(request):
#     logout(request)
#     messages.success(request, 'You have been logged out.')
#     return redirect('login')

# auth_app/views/logout_views.py

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required # Ensures only logged-in users can access this view
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login') # Redirect to login page or homepage (ensure 'login' is a valid URL name)