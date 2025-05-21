# job_portal/views/api_usage_status_view.py

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

from job_portal.models import APIUsage


@login_required
def get_ai_usage_stats(request):
    """
    Get AI usage statistics for the current user.
    Returns a JSON response with usage data.
    """
    # Get time period from request
    period = request.GET.get('period', 'month')  # 'day', 'week', 'month', 'all'

    # Calculate date filter based on period
    if period == 'day':
        start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start_date = timezone.now() - timezone.timedelta(days=7)
    elif period == 'month':
        start_date = timezone.now() - timezone.timedelta(days=30)
    else:  # 'all'
        start_date = None

    # Query API usage
    query = APIUsage.objects.filter(user=request.user)
    if start_date:
        query = query.filter(timestamp__gte=start_date)

    # Aggregate by API type
    chatgpt_usage = query.filter(api_name='chatgpt')
    gemini_usage = query.filter(api_name='gemini')

    # Calculate totals
    chatgpt_cost = sum([float(usage.cost) for usage in chatgpt_usage])
    gemini_cost = sum([float(usage.cost) for usage in gemini_usage])
    chatgpt_tokens = sum([usage.total_tokens or 0 for usage in chatgpt_usage])
    gemini_tokens = sum([usage.total_tokens or 0 for usage in gemini_usage])

    # Count operations
    operation_counts = {}
    operation_types = set(op[0] for op in APIUsage.OPERATION_TYPES)
    for op_code in operation_types:
        operation_counts[op_code] = query.filter(operation=op_code).count()

    # Prepare response data
    data = {
        'period': period,
        'usage': {
            'chatgpt': {
                'cost': str(chatgpt_cost),
                'tokens': chatgpt_tokens,
                'count': chatgpt_usage.count()
            },
            'gemini': {
                'cost': str(gemini_cost),
                'tokens': gemini_tokens,
                'count': gemini_usage.count()
            }
        },
        'operations': operation_counts,
        'total_cost': str(chatgpt_cost + gemini_cost),
        'total_requests': query.count()
    }

    return JsonResponse(data)

# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# from django.utils import timezone
#
# from job_portal.models import (
#     APIUsage
# )
#
#
# @login_required
# def get_ai_usage_stats(request):
#     """
#     Get AI usage statistics for the current user.
#     Returns a JSON response with usage data.
#     """
#     # Get time period from request
#     period = request.GET.get('period', 'month')  # 'day', 'week', 'month', 'all'
#
#     # Calculate date filter based on period
#     if period == 'day':
#         start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
#     elif period == 'week':
#         start_date = timezone.now() - timezone.timedelta(days=7)
#     elif period == 'month':
#         start_date = timezone.now() - timezone.timedelta(days=30)
#     else:  # 'all'
#         start_date = None
#
#     # Query API usage
#     query = APIUsage.objects.filter(user=request.user)
#     if start_date:
#         query = query.filter(timestamp__gte=start_date)
#
#     # Aggregate by API type
#     chatgpt_usage = query.filter(api_name='chatgpt')
#     gemini_usage = query.filter(api_name='gemini')
#
#     # Calculate totals
#     chatgpt_cost = sum([usage.cost for usage in chatgpt_usage])
#     gemini_cost = sum([usage.cost for usage in gemini_usage])
#     chatgpt_tokens = sum([usage.total_tokens for usage in chatgpt_usage])
#     gemini_tokens = sum([usage.total_tokens for usage in gemini_usage])
#
#     # Count operations
#     operation_counts = {}
#     for op in APIUsage.OPERATION_TYPES:
#         op_code = op[0]
#         operation_counts[op_code] = query.filter(operation=op_code).count()
#
#     # Prepare response data
#     data = {
#         'period': period,
#         'usage': {
#             'chatgpt': {
#                 'cost': str(chatgpt_cost),
#                 'tokens': chatgpt_tokens,
#                 'count': chatgpt_usage.count()
#             },
#             'gemini': {
#                 'cost': str(gemini_cost),
#                 'tokens': gemini_tokens,
#                 'count': gemini_usage.count()
#             }
#         },
#         'operations': operation_counts,
#         'total_cost': str(chatgpt_cost + gemini_cost),
#         'total_requests': query.count()
#     }
#
#     return JsonResponse(data)
