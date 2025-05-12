# # resumes/views.py
# import json
# import os
# import tempfile
#
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from django.shortcuts import redirect, render, get_object_or_404
# from django.views.decorators.http import require_http_methods
#
# from job_portal.models import (
#     Resume, Skill, Experience, ExperienceBulletPoint,
#     Education, Certification, Project, ProjectBulletPoint,
#     Language, CustomData, APIUsage
# )
# from services.bullets_ai_services import generate_bullets_chatgpt, get_template_bullets, generate_bullets_gemini, \
#     enhance_bullet_chatgpt, enhance_bullet_gemini, enhance_bullet_basic, ats_optimize_chatgpt, ats_optimize_gemini
# from ..forms.resume_creation_form import ResumeBasicInfoForm, ResumeSummaryForm
# from ..forms.resume_upload_form import ResumeUploadForm
# from ..models import (
#     JobInput
# )
# from django.contrib.auth.decorators import login_required
#
# @login_required
# def view_resume(request, resume_id):
#     """View the generated resume."""
#     resume = get_object_or_404(Resume, id=resume_id, user=request.user)
#     template_id = request.GET.get('template', 1)  # Default to template 1
#
#     context = {
#         'resume': resume,
#         'template_id': template_id,
#     }
#
#     return render(request, f'resumes/templates/template{template_id}.html', context)