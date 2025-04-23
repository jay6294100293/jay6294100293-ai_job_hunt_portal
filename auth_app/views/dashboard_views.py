from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from job_portal.models import Resume # Import the Resume model

@login_required
def dashboard_view(request):
    # Fetch user's resumes
    user_resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
    resume_count = user_resumes.count()
    recent_resumes = user_resumes[:5] # Get latest 5

    context = {
        'resume_count': resume_count,
        'recent_resumes': recent_resumes,
        # Add other context data as needed (e.g., application count when implemented)
        'user': request.user # Pass the user object for API key checks in template
    }
    # Ensure you render the *new* dashboard template path if you moved it
    return render(request, 'auth/dashboard.html', context)

#
# from django.shortcuts import render
#
#
# def dashboard_view(request):
#     # You can add any context data to pass to the dashboard template
#     context = {
#         # Example of any data you may want to pass
#         'user_name': request.user.username,
#         # Add more context data as necessary
#     }
#     return render(request, 'auth/dashboard.html', context)