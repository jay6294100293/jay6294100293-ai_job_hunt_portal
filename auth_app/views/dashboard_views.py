# auth_app/views/dashboard_views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from job_portal.models import Resume # Assuming job_portal app and Resume model exist

@login_required
def dashboard_view(request):
    # Fetch user's resumes
    # Ensure job_portal.models.Resume is correctly defined and migrated.
    try:
        user_resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
        resume_count = user_resumes.count()
        recent_resumes = user_resumes[:5] # Get latest 5
    except Exception as e: # Fallback in case Resume model or query fails
        user_resumes = []
        resume_count = 0
        recent_resumes = []
        # messages.warning(request, f"Could not load resume data: {e}") # Optional: inform admin or user

    context = {
        'resume_count': resume_count,
        'recent_resumes': recent_resumes,
        # Add other context data as needed (e.g., application count when implemented)
        'user': request.user # Pass the user object for API key checks in template
    }
    # Ensure your template path 'auth/dashboard.html' is correct.
    return render(request, 'auth/dashboard.html', context)

# from django.shortcuts import render


# from django.contrib.auth.decorators import login_required
# from job_portal.models import Resume # Import the Resume model
#
# @login_required
# def dashboard_view(request):
#     # Fetch user's resumes
#     user_resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
#     resume_count = user_resumes.count()
#     recent_resumes = user_resumes[:5] # Get latest 5
#
#     context = {
#         'resume_count': resume_count,
#         'recent_resumes': recent_resumes,
#         # Add other context data as needed (e.g., application count when implemented)
#         'user': request.user # Pass the user object for API key checks in template
#     }
#     # Ensure you render the *new* dashboard template path if you moved it
#     return render(request, 'auth/dashboard.html', context)
#
# #
# # from django.shortcuts import render
# #
# #
# # def dashboard_view(request):
# #     # You can add any context data to pass to the dashboard template
# #     context = {
# #         # Example of any data you may want to pass
# #         'user_name': request.user.username,
# #         # Add more context data as necessary
# #     }
# #     return render(request, 'auth/dashboard.html', context)