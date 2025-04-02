# auth_app/urls.py

from django.conf.urls.static import static
from django.urls import path

from ai_job_hunt_portal import settings
from job_portal.forms.resume_creation_form import load_more_skills
from job_portal.views.resume_create_view import template_selection, select_template, resume_wizard, generate_resume, \
    view_resume, download_resume, resume_list, edit_resume, delete_resume, update_resume_ajax, htmx_add_form_row, \
    preview_template, preview_current_resume, get_language_template, ai_generate_bullets, enhance_bullet, \
    check_bullet_strength, get_ai_usage_stats

app_name = 'job_portal'
urlpatterns = [
    # AI-related endpoints
    path('ai/generate-bullets/', ai_generate_bullets, name='ai_generate_bullets'),
    path('ai/enhance-bullet/', enhance_bullet, name='enhance_bullet'),
    path('ai/check-bullet-strength/', check_bullet_strength, name='check_bullet_strength'),
    path('ai/usage-stats/', get_ai_usage_stats, name='get_ai_usage_stats'),
# AI-powered features

    path('get-language-template/', get_language_template, name='get_language_template'),
    # Template selection
    path('', template_selection, name='template_selection'),
    path('select-template/', select_template, name='select_template'),

    path('load-more-skills/', load_more_skills, name='load_more_skills'),
    path('preview-current-resume/', preview_current_resume, name='preview_current_resume'),
    # Resume wizard
    path('wizard/<str:step>/', resume_wizard, name='resume_wizard'),
    path('htmx/add-form-row/', htmx_add_form_row, name='htmx_add_form_row'),
    # Resume generation and management
    path('generate/', generate_resume, name='generate_resume'),
    path('view/<int:resume_id>/', view_resume, name='view_resume'),
    path('download/<int:resume_id>/', download_resume, name='download_resume'),
    path('list/', resume_list, name='resume_list'),
    path('edit/<int:resume_id>/', edit_resume, name='edit_resume'),
    path('delete/<int:resume_id>/', delete_resume, name='delete_resume'),

    # AJAX handlers
    path('update/<int:resume_id>/', update_resume_ajax, name='update_resume_ajax'),
    path('preview-template/<int:template_id>/', preview_template, name='preview_template'),
    # HTMX handlers
    path('resumes/htmx/add-form-row/', htmx_add_form_row, name='htmx_add_form_row'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)