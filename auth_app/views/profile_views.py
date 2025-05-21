# auth_app/views/profile_views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from auth_app.forms.profile_update_form import ProfileUpdateForm


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(instance=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _("Your profile has been updated successfully."))
            return redirect('profile')  # Adjust redirect as needed
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        form = ProfileUpdateForm(instance=request.user)

    context = {
        'form': form,
        'user': request.user,
    }

    return render(request, 'auth/profile.html', context)


@login_required
def view_profile(request):
    context = {
        'user': request.user,
    }
    return render(request, 'auth/view_profile.html', context)