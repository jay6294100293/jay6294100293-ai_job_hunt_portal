
from django.shortcuts import render


def dashboard_view(request):
    # You can add any context data to pass to the dashboard template
    context = {
        # Example of any data you may want to pass
        'user_name': request.user.username,
        # Add more context data as necessary
    }
    return render(request, 'auth/dashboard.html', context)