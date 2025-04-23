from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# job_portal/views/resume_create_view.py (add this function)

@login_required
def resume_creation_choice(request):
    """
    Display a page for users to choose between creating a new resume or uploading an existing one.
    """
    return render(request, 'resumes/resume_creation_choice.html')