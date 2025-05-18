# # ai_job_web/auth_app/views/api_key_views.py
#
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
#
# from auth_app.forms.api_update_key_form import ApiKeyUpdateForm
#
#
# @login_required
# def update_api_keys(request):
#     if request.method == 'POST':
#         form = ApiKeyUpdateForm(instance=request.user, data=request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "API keys updated successfully.")
#             return redirect('update_api_keys')  # Redirect to the same page or any other
#     else:
#         form = ApiKeyUpdateForm(instance=request.user)
#
#     return render(request, 'auth/update_api_keys.html', {'form': form})


# auth_app/views/api_key_views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from auth_app.forms.api_update_key_form import ApiKeyUpdateForm


@login_required
def update_api_keys(request):
    if request.method == 'POST':
        # Pass request.user as the instance to update the current user's API keys
        form = ApiKeyUpdateForm(instance=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "API keys updated successfully.")
            # Redirect to the same page (or dashboard, or wherever appropriate)
            return redirect('update_api_keys')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ApiKeyUpdateForm(instance=request.user)

    return render(request, 'auth/update_api_keys.html', {'form': form})