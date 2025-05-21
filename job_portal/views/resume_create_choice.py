# job_portal/views/resume_create_choice.py

from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib import messages

from job_portal.models import Resume


class ResumeCreateChoiceView(LoginRequiredMixin, View):
    template_name = 'resumes/resume_creation_choice.html'

    def get(self, request, *args, **kwargs):
        """
        Displays the choice page: create from scratch or upload.
        """
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        """
        Handles the user's choice: 'scratch' or 'upload'.
        """
        create_choice = request.POST.get('create_choice')

        if create_choice == 'scratch':
            # User chose to create a resume from scratch.
            # Redirect to meta info form (title and template)
            return redirect(reverse('job_portal:create_resume_meta'))

        elif create_choice == 'upload':
            # User chose to upload a resume.
            return redirect(reverse('job_portal:upload_resume'))
        else:
            # An invalid choice was submitted.
            messages.error(request, "Invalid choice. Please select an option to proceed.")
            return render(request, self.template_name)

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
#
#
# # job_portal/views/resume_create_view.py (add this function)
#
# @login_required
# def resume_creation_choice(request):
#     """
#     Display a page for users to choose between creating a new resume or uploading an existing one.
#     """
#     return render(request, 'resumes/resume_creation_choice.html')