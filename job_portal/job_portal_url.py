from django.conf.urls.static import static
from django.urls import path

from ai_job_hunt_portal import settings
from job_portal.forms.resume_creation_form import load_more_skills
from job_portal.views.api_usage_status_view import get_ai_usage_stats
from job_portal.views.download_resume_view import download_resume
from job_portal.views.experience_enhancement_view import ai_generate_bullets, enhance_bullet, check_bullet_strength
from job_portal.views.generate_resume_view import generate_resume
from job_portal.views.htmx_add_form_view import htmx_add_form_row
from job_portal.views.modification_resume_view import resume_list, edit_resume, delete_resume, update_resume_ajax
from job_portal.views.preview_current_resume_view import preview_current_resume
from job_portal.views.project_enhancement_view import enhance_project_bullet, project_bullet_enhancement_form
from job_portal.views.resume_create_choice import resume_creation_choice
from job_portal.views.resume_upload_view import upload_resume, edit_resume_section, \
    save_resume_section, preview_upload_data
from job_portal.views.template_selection_view import template_selection, select_template, resume_wizard
from job_portal.views.view_resume_view import view_resume
from services.supporting_codes.resume_support_code import get_language_template, preview_template

app_name = 'job_portal'
urlpatterns = [

    path('', resume_creation_choice, name='resume_creation_choice'),
    path('enhance-project-bullet/', enhance_project_bullet, name='enhance_project_bullet'),
    path('project-enhancement-form/', project_bullet_enhancement_form, name='project_bullet_enhancement_form'),
    # Add these new paths
    path('upload-resume/', upload_resume, name='upload_resume'),
    #path('create-from-upload/', create_resume_from_upload, name='create_resume_from_upload'),
    path('edit-section/<int:resume_id>/<str:section>/', edit_resume_section, name='edit_resume_section'),
    path('save-section/<int:resume_id>/', save_resume_section, name='save_resume_section'),
    path('preview-upload-data/', preview_upload_data, name='preview_upload_data'),

    # Keep the template selection URL but make it a separate path
    path('template-selection/', template_selection, name='template_selection'),
    # AI-related endpoints
    path('ai/generate-bullets/', ai_generate_bullets, name='ai_generate_bullets'),
    path('ai/enhance-bullet/', enhance_bullet, name='enhance_bullet'),
    path('ai/check-bullet-strength/', check_bullet_strength, name='check_bullet_strength'),
    path('ai/usage-stats/', get_ai_usage_stats, name='get_ai_usage_stats'),
# AI-powered features

    path('get-language-template/', get_language_template, name='get_language_template'),
    # Template selection
    # path('', template_selection, name='template_selection'),
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