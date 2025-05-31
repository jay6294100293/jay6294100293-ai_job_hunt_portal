# File: job_portal/views/modification_resume_view.py
# Path: job_portal/views/modification_resume_view.py

import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _  # For internationalization of messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from job_portal.models import (  #
    Resume, Skill, Experience, Education, Certification, Project, Language, CustomData,  #
    ExperienceBulletPoint, ProjectBulletPoint  #
)
from job_portal.forms.resume_creation_form import (  #
    ResumeMetaForm, ResumeBasicInfoForm, ResumeSummaryForm,  #
    ExperienceInlineFormSet, EducationInlineFormSet, SkillInlineFormSet,  #
    ProjectInlineFormSet, CertificationInlineFormSet, LanguageInlineFormSet,  #
    CustomDataInlineFormSet,  #
    ExperienceBulletPointInlineFormSet, ProjectBulletPointInlineFormSet  #
)
from job_portal.forms.resume_upload_form import ResumeUploadForm  #

logger = logging.getLogger(__name__)  #


@login_required
@require_POST
@csrf_protect
def set_primary_resume_view(request, resume_id):
    """Set a resume as the primary resume for the user."""
    try:
        # Get the resume and ensure it belongs to the current user
        resume = get_object_or_404(Resume, id=resume_id, user=request.user)

        with transaction.atomic():
            # Unset all other resumes as primary for this user
            Resume.objects.filter(user=request.user, is_primary=True).update(is_primary=False)

            # Set this resume as primary
            resume.is_primary = True
            resume.save()

        messages.success(request, f'"{resume.title}" has been set as your primary resume.')

        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'"{resume.title}" has been set as your primary resume.'
            })

        return redirect('job_portal:resume_list')

    except Exception as e:
        messages.error(request, 'An error occurred while setting the primary resume.')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'An error occurred while setting the primary resume.'
            })

        return redirect('job_portal:resume_list')


@login_required
def resume_wizard_view(request, resume_id, step):
    """Resume wizard view for step-by-step editing."""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    # Define valid steps
    valid_steps = ['personal_info', 'experience', 'education', 'skills', 'projects', 'summary']

    if step not in valid_steps:
        messages.error(request, 'Invalid step specified.')
        return redirect('job_portal:resume_list')

    # For now, redirect to the edit section view with the section slug
    return redirect('job_portal:edit_resume_section', resume_id=resume_id, section_slug=step)
# --- Resume List and Deletion ---
@login_required  #
def resume_list_view(request):  #
    """List all resumes created by the user."""  #
    resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')  #
    return render(request, 'resumes/resume_list.html', {'resumes': resumes})  #


@login_required  #
def delete_resume_view(request, resume_id):  #
    """Deletes a resume after confirmation."""  #
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)  #
    if request.method == 'POST':  #
        title = resume.title  #
        resume.delete()  #
        messages.success(request,
                         _("Resume '{title}' deleted successfully.").format(title=title))  # Use a translatable string #
        return redirect('job_portal:resume_list')  #
    return render(request, 'resumes/confirm_delete.html', {'object': resume, 'object_type': 'Resume'})  #


# --- Resume Creation (New from Scratch) ---
@login_required  #
def create_resume_meta_view(request):  #
    """
    Creates the initial Resume object (title, publication status, visibility)
    when creating a resume from scratch. A default template is assigned by the model.
    Then, redirects to template selection.
    """
    if request.method == 'POST':  #
        form = ResumeMetaForm(request.POST)  # Uses ResumeMetaForm (without template_name field) #
        if form.is_valid():  #
            resume = form.save(commit=False)  #
            resume.user = request.user  #
            # 'title', 'publication_status', 'visibility' are set by the form.
            # 'template_name' will use the model's default value.

            # UPDATED: Use the correct status value from Resume.STATUS_CHOICES
            resume.status = 'created'  # This matches 'Created from Scratch' in your model

            resume.save()  #

            messages.success(request,
                             _("Resume details '{title}' saved. Now, please select a template.").format(
                                 title=resume.title))  # Message updated for new flow
            # UPDATED: Redirect to template selection view
            return redirect('job_portal:select_template', resume_id=resume.id)
        else:  #
            messages.error(request,
                           _("There was an issue with your submission. Please check the details below."))  # Use translatable string #
    else:  #
        # Model defaults are used for template_name, publication_status, and visibility.
        # Can provide 'initial' data to override form display defaults if needed.
        form = ResumeMetaForm(initial={
            # 'publication_status': Resume.DRAFT, # Model default is DRAFT
            # 'visibility': Resume.VISIBILITY_PRIVATE, # Model default is PRIVATE
        })
    return render(request, 'resumes/create_resume_meta.html', {'form': form})  #


# --- Resume Editing Wizard/Sections (Unified View) ---
def get_section_form_or_formset(section_slug, resume_instance, request_data=None, request_files=None):  #
    """Helper function to instantiate the correct form/formset for a given section."""  #
    prefixes = {  #
        'meta-info': 'meta', 'personal-info': 'pinfo', 'summary': 'summ',  #
        'experience': 'exp', 'education': 'edu', 'skills': 'skill',  #
        'projects': 'proj', 'certifications': 'cert', 'languages': 'lang',  #
        'custom-data': 'custom'  #
    }
    prefix = prefixes.get(section_slug)  #

    if section_slug == 'meta-info':  #
        return ResumeMetaForm(request_data, instance=resume_instance, prefix=prefix)  #
    elif section_slug == 'personal-info':  #
        return ResumeBasicInfoForm(request_data, request_files, instance=resume_instance, prefix=prefix)  #
    elif section_slug == 'summary':  #
        return ResumeSummaryForm(request_data, instance=resume_instance, prefix=prefix)  #
    elif section_slug == 'experience':  #
        return ExperienceInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)  #
    elif section_slug == 'education':  #
        return EducationInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)  #
    elif section_slug == 'skills':  #
        return SkillInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)  #
    elif section_slug == 'projects':  #
        return ProjectInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)  #
    elif section_slug == 'certifications':  #
        return CertificationInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)  #
    elif section_slug == 'languages':  #
        return LanguageInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)  #
    elif section_slug == 'custom-data':  #
        return CustomDataInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)  #
    return None  #


@login_required  #
def edit_resume_section_view(request, resume_id, section_slug):  #
    """View to edit a specific section of a resume, saving changes directly to the database."""  #
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)  #

    section_flow = [  #
        'meta-info', 'personal-info', 'summary', 'experience', 'education',  #
        'skills', 'projects', 'certifications', 'languages', 'custom-data'  #
    ]

    form_or_formset = get_section_form_or_formset(section_slug, resume, request.POST or None, request.FILES or None)  #

    if form_or_formset is None:  #
        logger.error(f"No form/formset found for section_slug: {section_slug} with resume_id: {resume_id}")  #
        raise Http404(_("Invalid resume section specified: {}").format(section_slug))  #

    try:  #
        current_section_index = section_flow.index(section_slug)  #
    except ValueError:  #
        logger.warning(f"Section slug '{section_slug}' not found in defined section_flow for resume ID {resume_id}.")  #
        current_section_index = -1  #

    next_section_slug = section_flow[
        current_section_index + 1] if current_section_index != -1 and current_section_index < len(
        section_flow) - 1 else None  #
    prev_section_slug = section_flow[
        current_section_index - 1] if current_section_index != -1 and current_section_index > 0 else None  #

    if request.method == 'POST':  #
        if form_or_formset.is_valid():  #
            with transaction.atomic():  #
                form_or_formset.save()  #
                resume.updated_at = timezone.now()  #
                resume.save()  #
            messages.success(request, _("{section_name} section updated successfully.").format(
                section_name=section_slug.replace('-', ' ').title()))  #

            action = request.POST.get('action', 'save_and_continue')  #
            if action == 'save_and_next' and next_section_slug:  #
                return redirect('job_portal:edit_resume_section', resume_id=resume.id,
                                section_slug=next_section_slug)  #
            elif action == 'save_and_exit':  #
                return redirect('job_portal:view_resume', resume_id=resume.id)  #
            return redirect('job_portal:edit_resume_section', resume_id=resume.id, section_slug=section_slug)  #
        else:  #
            error_message_detail = ""  #
            if hasattr(form_or_formset, 'errors') and form_or_formset.errors:  #
                error_message_detail = _(" Errors: {}").format(form_or_formset.errors.as_text())  #
            elif hasattr(form_or_formset, 'non_form_errors') and form_or_formset.non_form_errors():  #
                error_message_detail = _(" Errors: {}").format(form_or_formset.non_form_errors().as_text())  #

            if hasattr(form_or_formset, 'forms'):  # For formsets, collect individual form errors #
                for i, form_in_fs in enumerate(form_or_formset.forms):  #
                    if form_in_fs.errors:  #
                        form_errors = " ".join([_("Item {item_num} - {field}: {errors}").format(  #
                            item_num=i + 1, field=field, errors=", ".join(errs)  #
                        ) for field, errs in form_in_fs.errors.items()])  #
                        error_message_detail += f" {form_errors}".strip()  #

            messages.error(request,
                           _("Please correct the errors in the {section_name} section.{error_detail}").format(  #
                               section_name=section_slug.replace('-', ' ').title(),  #
                               error_detail=error_message_detail.strip()  #
                           ))

    template_name_base = section_slug.replace("-", "_")  #
    template_name = f'resumes/wizard_steps/{template_name_base}.html'  #

    context = {  #
        'resume': resume,  #
        'form_or_formset': form_or_formset,  #
        'section_slug': section_slug,  #
        'section_title': section_slug.replace('-', ' ').title(),  #
        'next_section_slug': next_section_slug,  #
        'prev_section_slug': prev_section_slug,  #
        'wizard_base_template': 'resumes/wizard_base.html',  # Main wizard layout #
        'is_final_section': section_slug == section_flow[-1],  #
    }
    return render(request, template_name, context)  #


# --- Resume Upload and Direct DB Population ---
def _populate_resume_from_parsed_data(resume_instance, parsed_data_dict):  #
    """
    Helper to populate a Resume instance and its related objects from parsed data.
    This function expects `parsed_data_dict` to have keys matching model sections
    and list of dictionaries for items within those sections.
    It assumes field names in parsed_data_dict items mostly match model field names.
    """  #
    with transaction.atomic():  #
        # Personal Info (direct fields on Resume)
        p_info = parsed_data_dict.get('personal_info', {})  #
        for field, value in p_info.items():  #
            if hasattr(resume_instance, field) and value is not None:  #
                setattr(resume_instance, field, value)  #

        # Summary (direct field on Resume)
        summary_text = parsed_data_dict.get('summary', {}).get('summary_text', '')  #
        if summary_text:  #
            resume_instance.summary = summary_text  #

        # UPDATED: Set status for uploaded resume using the correct value
        resume_instance.status = 'uploaded'  # This matches 'Populated from Upload' in your model
        resume_instance.save()  # Save personal info, summary, and status first #

        # Helper to populate related items
        def populate_related(model_class, data_key, foreign_key_field='resume'):  #
            related_manager = getattr(resume_instance, model_class._meta.get_field(foreign_key_field).related_name)  #
            related_manager.all().delete()  # Clear existing before adding new from parse #
            items_data = parsed_data_dict.get(data_key, [])  #
            for item_data in items_data:  #
                if not item_data: continue  # Skip empty items #

                # Handle bullet points for Experience and Project if present
                bullets_data = None  #
                bullet_point_model = None  #
                bullet_fk_field = None  #

                if data_key == 'experiences' and 'bullet_points' in item_data:  #
                    bullets_data = item_data.pop('bullet_points', [])  #
                    bullet_point_model = ExperienceBulletPoint  #
                    bullet_fk_field = 'experience'  #
                elif data_key == 'projects' and 'bullet_points' in item_data:  #
                    bullets_data = item_data.pop('bullet_points', [])  #
                    bullet_point_model = ProjectBulletPoint  #
                    bullet_fk_field = 'project'  #

                # Filter out keys not in model to prevent errors with **item_data
                valid_fields = {f.name for f in model_class._meta.get_fields() if f.concrete and not f.is_relation}  #
                filtered_item_data = {k: v for k, v in item_data.items() if k in valid_fields}  #

                if filtered_item_data:  # Ensure there's something to save #
                    obj_kwargs = {foreign_key_field: resume_instance, **filtered_item_data}  #
                    obj = model_class.objects.create(**obj_kwargs)  #

                    if bullets_data and bullet_point_model and bullet_fk_field:  #
                        for bullet_text in bullets_data:  #
                            if isinstance(bullet_text, str) and bullet_text.strip():  #
                                bullet_point_model.objects.create(
                                    **{bullet_fk_field: obj, 'description': bullet_text.strip()})  #
                            elif isinstance(bullet_text, dict) and bullet_text.get('description', '').strip():  #
                                bullet_point_model.objects.create(
                                    **{bullet_fk_field: obj, 'description': bullet_text.get('description').strip()})  #

        populate_related(Experience, 'experiences')  #
        populate_related(Education, 'education')  #
        populate_related(Skill, 'skills')  #
        populate_related(Project, 'projects')  #
        populate_related(Certification, 'certifications')  #
        populate_related(Language, 'languages')  #
        populate_related(CustomData, 'custom_data')  # Ensure 'custom_data' matches your parser's output key #


# --- Deleting items from formsets (HTMX/AJAX) ---
@login_required  #
def htmx_delete_section_item_view(request, resume_id, section_slug, item_id):  #
    """Deletes an item from a section (e.g., an experience entry) via HTMX."""  #
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)  #

    if request.method not in ['POST', 'DELETE']:  # HTMX might send DELETE as POST #
        return HttpResponseForbidden("Invalid request method.")  #

    item_model_map = {  #
        'experience': Experience, 'education': Education, 'skills': Skill,  #
        'projects': Project, 'certifications': Certification, 'languages': Language,  #
        'custom-data': CustomData  #
    }
    ModelClass = item_model_map.get(section_slug)  #
    if not ModelClass:  #
        logger.warning(f"Invalid section slug '{section_slug}' for HTMX deletion, resume ID {resume_id}.")  #
        raise Http404("Invalid section for deletion.")  #

    try:  #
        # Ensure the item belongs to the specified resume before deleting
        item_to_delete = get_object_or_404(ModelClass, id=item_id, resume=resume)  #
        item_to_delete.delete()  #
        # For HTMX, an empty 200 OK or 204 No Content response is sufficient
        # if the client-side script handles removing the element.
        return HttpResponse("", status=200)  #
    except Http404:  #
        logger.warning(  #
            f"Item ID {item_id} (section: {section_slug}) not found for resume {resume_id} during HTMX delete.",  #
            exc_info=True)
        return HttpResponse("Error: Item not found or permission denied.", status=404)  #
    except Exception as e:  #
        logger.error(f"Error deleting section item {item_id} from {section_slug} for resume {resume_id}: {e}",  #
                     exc_info=True)
        return HttpResponse(f"An unexpected error occurred: {e}", status=500)  #

# # job_portal/views/modification_resume_view.py
#
# import logging
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponse
# from django.shortcuts import render, redirect, get_object_or_404
# from django.urls import reverse
# from django.utils import timezone
#
# from job_portal.models import (
#     Resume, Skill, Experience, Education, Certification, Project, Language, CustomData,
#     ExperienceBulletPoint, ProjectBulletPoint
# )
# from job_portal.forms.resume_creation_form import (
#     ResumeMetaForm, ResumeBasicInfoForm, ResumeSummaryForm,
#     ExperienceInlineFormSet, EducationInlineFormSet, SkillInlineFormSet,
#     ProjectInlineFormSet, CertificationInlineFormSet, LanguageInlineFormSet,
#     CustomDataInlineFormSet,
#     ExperienceBulletPointInlineFormSet, ProjectBulletPointInlineFormSet
# )
# from job_portal.forms.resume_upload_form import ResumeUploadForm
#
# logger = logging.getLogger(__name__)
#
#
# # --- Resume List and Deletion ---
# @login_required
# def resume_list_view(request):
#     """List all resumes created by the user."""
#     resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
#     return render(request, 'resumes/resume_list.html', {'resumes': resumes})
#
#
# @login_required
# def delete_resume_view(request, resume_id):
#     """Deletes a resume after confirmation."""
#     resume = get_object_or_404(Resume, id=resume_id, user=request.user)
#     if request.method == 'POST':
#         title = resume.title
#         resume.delete()
#         messages.success(request, f"Resume '{title}' deleted successfully.")
#         return redirect('job_portal:resume_list')
#     return render(request, 'resumes/confirm_delete.html', {'object': resume, 'object_type': 'Resume'})
#
#
# # --- Resume Creation (New from Scratch) ---
# @login_required  #
# def create_resume_meta_view(request):  #
#     """
#     Creates the initial Resume object (title, publication status, visibility)
#     when creating a resume from scratch. A default template is assigned by the model.
#     """
#     if request.method == 'POST':  #
#         form = ResumeMetaForm(request.POST)  # Uses the updated ResumeMetaForm (without template_name)
#         if form.is_valid():  #
#             resume = form.save(commit=False)  #
#             resume.user = request.user  #
#             # 'title', 'publication_status', 'visibility' are set by the form.
#             # 'template_name' will use the model's default value ('template1').
#             resume.status = 'created_from_scratch'  # Set a specific status for this creation method.
#
#             resume.save()  #
#
#             messages.success(request,
#                              f"Draft resume '{resume.title}' created successfully. You can now add its sections.")  #
#             return redirect('job_portal:edit_resume_section', resume_id=resume.id, section_slug='personal-info')  #
#         else:  #
#             messages.error(request, "There was an issue with your submission. Please check the details below.")  #
#     else:  #
#         # The Resume model has defaults for:
#         # - template_name: 'template1'
#         # - publication_status: Resume.DRAFT
#         # - visibility: Resume.VISIBILITY_PRIVATE
#         # These will be used. You can override publication_status and visibility
#         # defaults here if needed for this specific form instance via the 'initial' dict.
#         form = ResumeMetaForm(initial={
#             # 'publication_status': Resume.DRAFT, # This is model default, explicit set is optional
#             # 'visibility': Resume.VISIBILITY_PRIVATE, # This is model default, explicit set is optional
#         })
#     return render(request, 'resumes/create_resume_meta.html', {'form': form})  #
#
#
# # --- Resume Editing Wizard/Sections (Unified View) ---
# def get_section_form_or_formset(section_slug, resume_instance, request_data=None, request_files=None):
#     """Helper function to instantiate the correct form/formset for a given section."""
#     prefixes = {
#         'meta-info': 'meta', 'personal-info': 'pinfo', 'summary': 'summ',
#         'experience': 'exp', 'education': 'edu', 'skills': 'skill',
#         'projects': 'proj', 'certifications': 'cert', 'languages': 'lang',
#         'custom-data': 'custom'
#     }
#     prefix = prefixes.get(section_slug)
#
#     if section_slug == 'meta-info':
#         return ResumeMetaForm(request_data, instance=resume_instance, prefix=prefix)
#     elif section_slug == 'personal-info':
#         return ResumeBasicInfoForm(request_data, request_files, instance=resume_instance, prefix=prefix)
#     elif section_slug == 'summary':
#         return ResumeSummaryForm(request_data, instance=resume_instance, prefix=prefix)
#     elif section_slug == 'experience':
#         return ExperienceInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)
#     elif section_slug == 'education':
#         return EducationInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)
#     elif section_slug == 'skills':
#         return SkillInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)
#     elif section_slug == 'projects':
#         return ProjectInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)
#     elif section_slug == 'certifications':
#         return CertificationInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)
#     elif section_slug == 'languages':
#         return LanguageInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)
#     elif section_slug == 'custom-data':
#         return CustomDataInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)
#     return None
#
#
# @login_required
# def edit_resume_section_view(request, resume_id, section_slug):
#     """View to edit a specific section of a resume, saving changes directly to the database."""
#     resume = get_object_or_404(Resume, id=resume_id, user=request.user)
#
#     # Define your wizard flow
#     section_flow = [
#         'meta-info', 'personal-info', 'summary', 'experience', 'education',
#         'skills', 'projects', 'certifications', 'languages', 'custom-data'
#     ]
#
#     form_or_formset = get_section_form_or_formset(section_slug, resume, request.POST or None, request.FILES or None)
#
#     if form_or_formset is None:
#         raise Http404(f"Invalid resume section specified: {section_slug}")
#
#     try:
#         current_section_index = section_flow.index(section_slug)
#     except ValueError:
#         current_section_index = -1
#
#     next_section_slug = section_flow[current_section_index + 1] if current_section_index != -1 and current_section_index < len(section_flow) - 1 else None
#     prev_section_slug = section_flow[current_section_index - 1] if current_section_index != -1 and current_section_index > 0 else None
#
#     if request.method == 'POST':
#         if form_or_formset.is_valid():
#             with transaction.atomic():
#                 form_or_formset.save()
#                 resume.updated_at = timezone.now()
#                 resume.save()
#             messages.success(request, f"{section_slug.replace('-', ' ').title()} section updated successfully.")
#
#             action = request.POST.get('action', 'save_and_continue')
#             if action == 'save_and_next' and next_section_slug:
#                 return redirect('job_portal:edit_resume_section', resume_id=resume.id, section_slug=next_section_slug)
#             elif action == 'save_and_exit':
#                 return redirect('job_portal:view_resume', resume_id=resume.id)
#             return redirect('job_portal:edit_resume_section', resume_id=resume.id, section_slug=section_slug)
#         else:
#             error_message_detail = ""
#             if hasattr(form_or_formset, 'errors') and form_or_formset.errors:
#                 error_message_detail = f" Errors: {form_or_formset.errors.as_text()}"
#             elif hasattr(form_or_formset, 'non_form_errors') and form_or_formset.non_form_errors():
#                 error_message_detail = f" Errors: {form_or_formset.non_form_errors().as_text()}"
#
#             messages.error(request, f"Please correct the errors in the {section_slug.replace('-', ' ').title()} section.{error_message_detail}")
#
#     template_name_base = section_slug.replace("-", "_")
#     template_name = f'resumes/wizard_steps/{template_name_base}.html'
#
#     context = {
#         'resume': resume,
#         'form_or_formset': form_or_formset,
#         'section_slug': section_slug,
#         'section_title': section_slug.replace('-', ' ').title(),
#         'next_section_slug': next_section_slug,
#         'prev_section_slug': prev_section_slug,
#         'wizard_base_template': 'resumes/wizard_base.html',  # Main wizard layout
#         'is_final_section': section_slug == section_flow[-1],
#     }
#     return render(request, template_name, context)
#
#
# # --- Resume Upload and Direct DB Population ---
# def _populate_resume_from_parsed_data(resume_instance, parsed_data_dict):
#     """
#     Helper to populate a Resume instance and its related objects from parsed data.
#     This function expects `parsed_data_dict` to have keys matching model sections
#     and list of dictionaries for items within those sections.
#     It assumes field names in parsed_data_dict items mostly match model field names.
#     """
#     with transaction.atomic():
#         # Personal Info (direct fields on Resume)
#         p_info = parsed_data_dict.get('personal_info', {})
#         for field, value in p_info.items():
#             if hasattr(resume_instance, field) and value is not None:
#                 setattr(resume_instance, field, value)
#
#         # Summary (direct field on Resume)
#         summary_text = parsed_data_dict.get('summary', {}).get('summary_text', '')
#         if summary_text:
#             resume_instance.summary = summary_text
#         resume_instance.save()
#
#         # Helper to populate related items
#         def populate_related(model_class, data_key, foreign_key_field='resume'):
#             related_manager = getattr(resume_instance, model_class._meta.get_field(foreign_key_field).related_name)
#             related_manager.all().delete()  # Clear existing before adding new from parse
#             items_data = parsed_data_dict.get(data_key, [])
#             for item_data in items_data:
#                 if not item_data: continue
#                 # Handle bullet points for Experience and Project if present
#                 bullets_data = None
#                 if data_key == 'experiences' and 'bullet_points' in item_data:
#                     bullets_data = item_data.pop('bullet_points', [])
#                 elif data_key == 'projects' and 'bullet_points' in item_data:
#                     bullets_data = item_data.pop('bullet_points', [])
#
#                 # Filter out keys not in model to prevent errors with **item_data
#                 valid_fields = {f.name for f in model_class._meta.get_fields()}
#                 filtered_item_data = {k: v for k, v in item_data.items() if k in valid_fields}
#
#                 if filtered_item_data:  # Ensure there's something to save
#                     obj = model_class.objects.create(**{foreign_key_field: resume_instance}, **filtered_item_data)
#
#                     if bullets_data and data_key == 'experiences':
#                         for bullet_text in bullets_data:
#                             ExperienceBulletPoint.objects.create(experience=obj, description=bullet_text)
#                     elif bullets_data and data_key == 'projects':
#                         for bullet_text in bullets_data:
#                             ProjectBulletPoint.objects.create(project=obj, description=bullet_text)
#
#         populate_related(Experience, 'experiences')
#         populate_related(Education, 'education')
#         populate_related(Skill, 'skills')
#         populate_related(Project, 'projects')
#         populate_related(Certification, 'certifications')
#         populate_related(Language, 'languages')
#         populate_related(CustomData, 'custom_data')
#
#
# # --- Deleting items from formsets (HTMX/AJAX) ---
# @login_required
# def htmx_delete_section_item_view(request, resume_id, section_slug, item_id):
#     """Deletes an item from a section (e.g., an experience entry) via HTMX."""
#     resume = get_object_or_404(Resume, id=resume_id, user=request.user)
#
#     if request.method not in ['POST', 'DELETE']:
#         return HttpResponseForbidden("Invalid request method.")
#
#     item_model_map = {
#         'experience': Experience, 'education': Education, 'skills': Skill,
#         'projects': Project, 'certifications': Certification, 'languages': Language,
#         'custom-data': CustomData
#     }
#     ModelClass = item_model_map.get(section_slug)
#     if not ModelClass:
#         raise Http404("Invalid section for deletion.")
#
#     try:
#         # Ensure the item belongs to the specified resume before deleting
#         item_to_delete = get_object_or_404(ModelClass, id=item_id, resume=resume)
#         item_to_delete.delete()
#         return HttpResponse("", status=200)
#     except Http404:
#         return HttpResponse("Error: Item not found or permission denied.", status=404)
#     except Exception as e:
#         logger.error(f"Error deleting section item {item_id} from {section_slug} for resume {resume_id}: {e}",
#                      exc_info=True)
#         return HttpResponse(f"Error: {e}", status=500)
#
# # # job_portal/views/modification_resume_view.py
# # import json
# # import logging
# # from django.contrib import messages
# # from django.contrib.auth.decorators import login_required
# # from django.db import transaction
# # from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponse
# # from django.shortcuts import render, redirect, get_object_or_404
# # from django.urls import reverse
# # from django.utils import timezone  # For setting published_at or similar timestamps
# #
# # from job_portal.models import (
# #     Resume, Skill, Experience, Education, Certification, Project, Language, CustomData,
# #     ExperienceBulletPoint, ProjectBulletPoint  # If handling their formsets directly here
# # )
# # from job_portal.forms.resume_creation_form import (
# #     ResumeMetaForm, ResumeBasicInfoForm, ResumeSummaryForm,
# #     ExperienceInlineFormSet, EducationInlineFormSet, SkillInlineFormSet,
# #     ProjectInlineFormSet, CertificationInlineFormSet, LanguageInlineFormSet,
# #     CustomDataInlineFormSet,
# #     # Import bullet point formsets if they are managed at this top level
# #     # ExperienceBulletPointInlineFormSet, ProjectBulletPointInlineFormSet
# # )
# # from job_portal.forms.resume_upload_form import ResumeUploadForm
# # # Assuming you have a service for parsing. Update the import path if necessary.
# #
# #
# # logger = logging.getLogger(__name__)
# #
# #
# # # --- Resume List and Deletion ---
# # @login_required
# # def resume_list_view(request):
# #     """List all resumes created by the user."""
# #     resumes = Resume.objects.filter(user=request.user).order_by('-updated_at')
# #     # Template 'resumes/resume_list.html' will display these.
# #     return render(request, 'resumes/resume_list.html', {'resumes': resumes})
# #
# #
# # @login_required
# # def delete_resume_view(request, resume_id):
# #     """Deletes a resume after confirmation."""
# #     resume = get_object_or_404(Resume, id=resume_id, user=request.user)
# #     if request.method == 'POST':
# #         title = resume.title
# #         resume.delete()
# #         messages.success(request, f"Resume '{title}' deleted successfully.")
# #         return redirect('job_portal:resume_list')  # Ensure this URL name is correct
# #     # Template 'resumes/confirm_delete.html' for GET request.
# #     return render(request, 'resumes/confirm_delete.html', {'object': resume, 'object_type': 'Resume'})
# #
# #
# # # --- Resume Creation (New from Scratch) ---
# # @login_required
# # def create_resume_meta_view(request):
# #     """Creates the initial Resume object (title, template) with 'draft' status."""
# #     if request.method == 'POST':
# #         form = ResumeMetaForm(request.POST, user=request.user)  # Pass user if form needs it for validation/choices
# #         if form.is_valid():
# #             resume = form.save(commit=False)
# #             resume.user = request.user
# #             resume.status = 'draft'  # Set initial status
# #             # Ensure template_name is being saved correctly if part of ResumeMetaForm
# #             # resume.template_name = form.cleaned_data.get('template_name', 'default_template')
# #             resume.save()
# #             messages.success(request, f"Draft resume '{resume.title}' created. Now add details.")
# #             return redirect('job_portal:edit_resume_section', resume_id=resume.id, section_slug='personal-info')
# #         else:
# #             messages.error(request, "Please correct the errors below.")
# #     else:
# #         form = ResumeMetaForm(user=request.user)  # Pass user if form needs it for choices, etc.
# #     # Template 'resumes/create_resume_meta.html'.
# #     return render(request, 'resumes/create_resume_meta.html', {'form': form})
# #
# #
# # # --- Resume Editing Wizard/Sections (Unified View) ---
# # def get_section_form_or_formset(section_slug, resume_instance, request_data=None, request_files=None):
# #     """Helper function to instantiate the correct form/formset for a given section."""
# #     prefixes = {  # Unique prefixes for each form/formset
# #         'meta-info': 'meta', 'personal-info': 'pinfo', 'summary': 'summ',
# #         'experience': 'exp', 'education': 'edu', 'skills': 'skill',
# #         'projects': 'proj', 'certifications': 'cert', 'languages': 'lang',
# #         'custom-data': 'custom'
# #     }
# #     prefix = prefixes.get(section_slug)
# #
# #     if section_slug == 'meta-info':
# #         return ResumeMetaForm(request_data, instance=resume_instance, prefix=prefix, user=resume_instance.user)
# #     elif section_slug == 'personal-info':
# #         return ResumeBasicInfoForm(request_data, request_files, instance=resume_instance, prefix=prefix)
# #     elif section_slug == 'summary':
# #         return ResumeSummaryForm(request_data, instance=resume_instance, prefix=prefix)
# #     elif section_slug == 'experience':
# #         return ExperienceInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)
# #     elif section_slug == 'education':
# #         return EducationInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)
# #     elif section_slug == 'skills':
# #         return SkillInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)
# #     elif section_slug == 'projects':
# #         return ProjectInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)
# #     elif section_slug == 'certifications':
# #         return CertificationInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)
# #     elif section_slug == 'languages':
# #         return LanguageInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)
# #     elif section_slug == 'custom-data':
# #         return CustomDataInlineFormSet(request_data, request_files, instance=resume_instance, prefix=prefix)
# #     return None
# #
# #
# # @login_required
# # def edit_resume_section_view(request, resume_id, section_slug):
# #     """View to edit a specific section of a resume, saving changes directly to the database."""
# #     resume = get_object_or_404(Resume, id=resume_id, user=request.user)
# #
# #     # Define your wizard flow. 'meta-info' added for completeness if title/template is editable.
# #     section_flow = [
# #         'meta-info', 'personal-info', 'summary', 'experience', 'education',
# #         'skills', 'projects', 'certifications', 'languages', 'custom-data'
# #     ]
# #
# #     form_or_formset = get_section_form_or_formset(section_slug, resume, request.POST or None, request.FILES or None)
# #
# #     if form_or_formset is None:
# #         raise Http404(f"Invalid resume section specified: {section_slug}")
# #
# #     try:
# #         current_section_index = section_flow.index(section_slug)
# #     except ValueError:
# #         current_section_index = -1  # Section might not be in the main defined flow
# #
# #     next_section_slug = section_flow[
# #         current_section_index + 1] if current_section_index != -1 and current_section_index < len(
# #         section_flow) - 1 else None
# #     prev_section_slug = section_flow[
# #         current_section_index - 1] if current_section_index != -1 and current_section_index > 0 else None
# #
# #     if request.method == 'POST':
# #         if form_or_formset.is_valid():
# #             with transaction.atomic():
# #                 form_or_formset.save()
# #                 resume.updated_at = timezone.now()  # Explicitly update timestamp
# #                 resume.save()
# #             messages.success(request, f"{section_slug.replace('-', ' ').title()} section updated successfully.")
# #
# #             action = request.POST.get('action', 'save_and_continue')
# #             if action == 'save_and_next' and next_section_slug:
# #                 return redirect('job_portal:edit_resume_section', resume_id=resume.id, section_slug=next_section_slug)
# #             elif action == 'save_and_exit':
# #                 return redirect('job_portal:view_resume', resume_id=resume.id)
# #             return redirect('job_portal:edit_resume_section', resume_id=resume.id, section_slug=section_slug)
# #         else:
# #             error_message_detail = ""
# #             if hasattr(form_or_formset, 'errors') and form_or_formset.errors:
# #                 error_message_detail = f" Errors: {form_or_formset.errors.as_text()}"
# #             elif hasattr(form_or_formset, 'non_form_errors') and form_or_formset.non_form_errors():
# #                 error_message_detail = f" Errors: {form_or_formset.non_form_errors().as_text()}"
# #
# #             messages.error(request,
# #                            f"Please correct the errors in the {section_slug.replace('-', ' ').title()} section.{error_message_detail}")
# #
# #     template_name_base = section_slug.replace("-", "_")
# #     # Ensure these template paths exist, e.g., 'resumes/wizard_steps/personal_info.html'
# #     template_name = f'resumes/wizard_steps/{template_name_base}.html'
# #
# #     context = {
# #         'resume': resume,
# #         'form_or_formset': form_or_formset,
# #         'section_slug': section_slug,
# #         'section_title': section_slug.replace('-', ' ').title(),
# #         'next_section_slug': next_section_slug,
# #         'prev_section_slug': prev_section_slug,
# #         'wizard_base_template': 'resumes/wizard_base.html',  # Main wizard layout
# #     }
# #     return render(request, template_name, context)
# #
# #
# # # --- Resume Upload and Direct DB Population ---
# # def _populate_resume_from_parsed_data(resume_instance, parsed_data_dict):
# #     """
# #     Helper to populate a Resume instance and its related objects from parsed data.
# #     This function expects `parsed_data_dict` to have keys matching model sections
# #     and list of dictionaries for items within those sections.
# #     It assumes field names in parsed_data_dict items mostly match model field names.
# #     """
# #     with transaction.atomic():
# #         # Personal Info (direct fields on Resume)
# #         p_info = parsed_data_dict.get('personal_info', {})
# #         for field, value in p_info.items():
# #             if hasattr(resume_instance, field) and value is not None:
# #                 setattr(resume_instance, field, value)
# #
# #         # Summary (direct field on Resume)
# #         summary_text = parsed_data_dict.get('summary', {}).get('summary_text', '')  # Or just 'summary'
# #         if summary_text:
# #             resume_instance.summary = summary_text
# #         resume_instance.save()  # Save personal info and summary
# #
# #         # Helper to populate related items
# #         def populate_related(model_class, data_key, foreign_key_field='resume'):
# #             related_manager = getattr(resume_instance, model_class._meta.get_field(foreign_key_field).related_name)
# #             related_manager.all().delete()  # Clear existing before adding new from parse
# #             items_data = parsed_data_dict.get(data_key, [])
# #             for item_data in items_data:
# #                 if not item_data: continue
# #                 # Handle bullet points for Experience and Project if present
# #                 bullets_data = None
# #                 if data_key == 'experiences' and 'bullet_points' in item_data:
# #                     bullets_data = item_data.pop('bullet_points', [])
# #                 elif data_key == 'projects' and 'bullet_points' in item_data:
# #                     bullets_data = item_data.pop('bullet_points', [])
# #
# #                 # Filter out keys not in model to prevent errors with **item_data
# #                 valid_fields = {f.name for f in model_class._meta.get_fields()}
# #                 filtered_item_data = {k: v for k, v in item_data.items() if k in valid_fields}
# #
# #                 if filtered_item_data:  # Ensure there's something to save
# #                     obj = model_class.objects.create(**{foreign_key_field: resume_instance}, **filtered_item_data)
# #
# #                     if bullets_data and data_key == 'experiences':
# #                         for bullet_text in bullets_data:
# #                             ExperienceBulletPoint.objects.create(experience=obj, bullet_point=bullet_text)
# #                     elif bullets_data and data_key == 'projects':
# #                         for bullet_text in bullets_data:
# #                             ProjectBulletPoint.objects.create(project=obj, bullet_point=bullet_text)
# #
# #         populate_related(Experience, 'experiences')
# #         populate_related(Education, 'education')  # Usually 'education' not 'educations' in parsed data
# #         populate_related(Skill, 'skills')
# #         populate_related(Project, 'projects')
# #         populate_related(Certification, 'certifications')
# #         populate_related(Language, 'languages')
# #         populate_related(CustomData, 'custom_data')  # Or 'custom_sections' if parser uses that
# #
# #
# # @login_required
# # def upload_resume_view(request):
# #     """Handles resume file upload, parsing, and direct population of a draft Resume in DB."""
# #     if request.method == 'POST':
# #         form = ResumeUploadForm(request.POST, request.FILES)
# #         if form.is_valid():
# #             uploaded_file = form.cleaned_data['resume_file']
# #             ai_engine_choice = form.cleaned_data['ai_engine']
# #
# #             temp_title = f"Draft from {uploaded_file.name[:50]}"
# #             resume = None  # Define resume here to use in except block if needed
# #             try:
# #                 with transaction.atomic():
# #                     resume = Resume.objects.create(
# #                         user=request.user, title=temp_title,
# #                         source_uploaded_file=uploaded_file,
# #                         is_source_uploaded=True, status='draft'
# #                     )
# #
# #                     # This service should return a dictionary of structured data and the raw text
# #                     parsed_data, raw_text = parse_resume_file_to_structured_data(
# #                         uploaded_file, ai_engine_choice, request.user
# #                     )
# #
# #                     resume.parsed_text_content = raw_text
# #                     resume.parsed_json_data = parsed_data  # Store the original parsed JSON for reference
# #                     resume.save()
# #
# #                     _populate_resume_from_parsed_data(resume, parsed_data)
# #
# #                 messages.success(request, "Resume uploaded and parsed. Review and edit your draft.")
# #                 return redirect('job_portal:edit_resume_section', resume_id=resume.id, section_slug='personal-info')
# #
# #             except Exception as e:
# #                 logger.error(f"Error processing uploaded resume {uploaded_file.name} for {request.user.username}: {e}",
# #                              exc_info=True)
# #                 if resume and resume.pk:
# #                     messages.warning(request,
# #                                      f"Resume '{resume.title}' created as draft, but an error occurred during data population: {e}. Please edit manually.")
# #                     return redirect('job_portal:edit_resume_section', resume_id=resume.id, section_slug='personal-info')
# #                 else:
# #                     messages.error(request, f"Could not process uploaded resume: {e}")
# #                 return redirect('job_portal:resume_creation_choice')
# #         else:
# #             messages.error(request, "There was an error with your upload. Please check the file and try again.")
# #     else:
# #         form = ResumeUploadForm()
# #     return render(request, 'resumes/upload_resume.html', {'form': form})
# #
# #
# # # --- Deleting items from formsets (HTMX example) ---
# # @login_required
# # def htmx_delete_section_item_view(request, resume_id, section_slug, item_id):
# #     """Deletes an item from a section (e.g., an experience entry) via HTMX."""
# #     resume = get_object_or_404(Resume, id=resume_id, user=request.user)
# #
# #     if request.method not in ['POST', 'DELETE']:  # HTMX often uses POST for DELETE
# #         return HttpResponseForbidden("Invalid request method.")
# #
# #     item_model_map = {
# #         'experience': Experience, 'education': Education, 'skills': Skill,
# #         'projects': Project, 'certifications': Certification, 'languages': Language,
# #         'custom-data': CustomData
# #     }
# #     ModelClass = item_model_map.get(section_slug)
# #     if not ModelClass:
# #         raise Http404("Invalid section for deletion.")
# #
# #     try:
# #         # Ensure the item belongs to the specified resume before deleting
# #         item_to_delete = get_object_or_404(ModelClass, id=item_id, resume=resume)
# #         item_to_delete.delete()
# #         # For HTMX, an empty 200 OK response means success, and client-side JS removes the element.
# #         # You could also return a success message snippet if your HTMX setup expects it.
# #         return HttpResponse("", status=200)
# #     except Http404:
# #         # This means item not found or not linked to this resume for this user
# #         return HttpResponse("Error: Item not found or permission denied.", status=404)
# #     except Exception as e:
# #         logger.error(f"Error deleting section item {item_id} from {section_slug} for resume {resume_id}: {e}",
# #                      exc_info=True)
# #         return HttpResponse(f"Error: {e}", status=500)
# #
# #
# # # # resumes/views.py
# # # import json
# # # import os
# # # import tempfile
# # #
# # # from django.contrib import messages
# # # from django.contrib.auth.decorators import login_required
# # # from django.db import transaction
# # # from django.http import JsonResponse
# # # from django.shortcuts import redirect, render, get_object_or_404
# # # from django.views.decorators.http import require_http_methods
# # #
# # # from job_portal.models import (
# # #     Resume, Skill, Experience, ExperienceBulletPoint,
# # #     Education, Certification, Project, ProjectBulletPoint,
# # #     Language, CustomData, APIUsage
# # # )
# # # from services.bullets_ai_services import generate_bullets_chatgpt, get_template_bullets, generate_bullets_gemini, \
# # #     enhance_bullet_chatgpt, enhance_bullet_gemini, enhance_bullet_basic, ats_optimize_chatgpt, ats_optimize_gemini
# # # # from ..forms.resume_creation_form import ResumeBasicInfoForm, ResumeSummaryForm
# # # from ..forms.resume_upload_form import ResumeUploadForm
# # # from ..models import (
# # #     JobInput
# # # )
# # # from django.contrib.auth.decorators import login_required
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # #
# # # @login_required
# # # def resume_list(request):
# # #     """List all resumes created by the user."""
# # #     resumes = Resume.objects.filter(user=request.user)
# # #     return render(request, 'resumes/resume_list.html', {'resumes': resumes})
# # #
# # #
# # # @login_required
# # # def edit_resume(request, resume_id):
# # #     """Edit an existing resume."""
# # #     resume = get_object_or_404(Resume, id=resume_id, user=request.user)
# # #
# # #     # Load resume data into session for the wizard
# # #     form_data = {}
# # #
# # #     # Personal Info
# # #     form_data['personal_info'] = {
# # #         'first_name': resume.first_name,
# # #         'mid_name': resume.mid_name,
# # #         'last_name': resume.last_name,
# # #         'email': resume.email,
# # #         'phone': resume.phone,
# # #         'address': resume.address,
# # #         'linkedin': resume.linkedin,
# # #         'github': resume.github,
# # #         'portfolio': resume.portfolio,
# # #     }
# # #
# # #     # Summary
# # #     form_data['summary'] = {
# # #         'summary': resume.summary,
# # #     }
# # #
# # #     # Skills
# # #     skills_data = []
# # #     for skill in resume.skills.all():
# # #         skills_data.append({
# # #             'skill_name': skill.skill_name,
# # #             'skill_type': skill.skill_type,
# # #             'proficiency_level': skill.proficiency_level,
# # #         })
# # #     form_data['skills'] = skills_data
# # #
# # #     experiences_data = []
# # #     for exp in resume.experiences.all():
# # #         bullet_points = [{'description': bp.description} for bp in exp.bullet_points.all()]
# # #         experiences_data.append({
# # #             'job_title': exp.job_title,
# # #             'employer': exp.employer,
# # #             'location': exp.location,
# # #             'start_date': exp.start_date,
# # #             'end_date': exp.end_date,
# # #             'is_current': exp.is_current,
# # #             'bullet_points': bullet_points,  # Now a list of dicts with description
# # #         })
# # #     form_data['experiences'] = experiences_data
# # #
# # #     # Education
# # #     educations_data = []
# # #     for edu in resume.educations.all():
# # #         educations_data.append({
# # #             'school_name': edu.school_name,
# # #             'location': edu.location,
# # #             'degree': edu.degree,
# # #             'degree_type': edu.degree_type,
# # #             'field_of_study': edu.field_of_study,
# # #             'graduation_date': edu.graduation_date,
# # #             'gpa': edu.gpa,
# # #         })
# # #     form_data['educations'] = educations_data
# # #
# # #     # Projects
# # #     projects_data = []
# # #     for proj in resume.projects.all():
# # #         bullet_points = [bp.description for bp in proj.bullet_points.all()]
# # #         projects_data.append({
# # #             'project_name': proj.project_name,
# # #             'summary': proj.summary,
# # #             'start_date': proj.start_date,
# # #             'completion_date': proj.completion_date,
# # #             'project_link': proj.project_link,
# # #             'github_link': proj.github_link,
# # #             'bullet_points': bullet_points,
# # #         })
# # #     form_data['projects'] = projects_data
# # #
# # #     # Certifications
# # #     certifications_data = []
# # #     for cert in resume.certifications.all():
# # #         certifications_data.append({
# # #             'name': cert.name,
# # #             'institute': cert.institute,
# # #             'completion_date': cert.completion_date,
# # #             'expiration_date': cert.expiration_date,
# # #             'score': cert.score,
# # #             'link': cert.link,
# # #             'description': cert.description,
# # #         })
# # #     form_data['certifications'] = certifications_data
# # #
# # #     # Languages
# # #     languages_data = []
# # #     for lang in resume.languages.all():
# # #         languages_data.append({
# # #             'language_name': lang.language_name,
# # #             'proficiency': lang.proficiency,
# # #         })
# # #     form_data['languages'] = languages_data
# # #
# # #     # Custom Sections
# # #     custom_sections_data = []
# # #     for section in resume.custom_data.all():
# # #         custom_sections_data.append({
# # #             'name': section.name,
# # #             'completion_date': section.completion_date,
# # #             'bullet_points': section.bullet_points,
# # #             'description': section.description,
# # #             'link': section.link,
# # #             'institution_name': section.institution_name,
# # #         })
# # #     form_data['custom_sections'] = custom_sections_data
# # #
# # #     # Store data in session
# # #     request.session['resume_form_data'] = form_data
# # #     request.session['resume_template_id'] = request.GET.get('template', '1')
# # #     request.session['edit_resume_id'] = resume_id
# # #
# # #     # Redirect to first step of wizard
# # #     return redirect('job_portal:resume_wizard', step=1)
# # #
# # #
# # # @login_required
# # # def delete_resume(request, resume_id):
# # #     """Delete a resume."""
# # #     resume = get_object_or_404(Resume, id=resume_id, user=request.user)
# # #
# # #     if request.method == 'POST':
# # #         resume.delete()
# # #         messages.success(request, "Resume deleted successfully")
# # #         return redirect('job_portal:resume_list')
# # #
# # #     return render(request, 'resumes/confirm_delete.html', {'resume': resume})
# # #
# # # @login_required
# # # @require_http_methods(["POST"])
# # # def update_resume_ajax(request, resume_id):
# # #     """AJAX handler for updating resume section."""
# # #     resume = get_object_or_404(Resume, id=resume_id, user=request.user)
# # #     section = request.POST.get('section')
# # #     data = json.loads(request.POST.get('data', '{}'))
# # #
# # #     try:
# # #         if section == 'personal_info':
# # #             for field, value in data.items():
# # #                 if hasattr(resume, field):
# # #                     setattr(resume, field, value)
# # #             resume.save()
# # #         elif section == 'skills':
# # #             # Clear existing skills and add new ones
# # #             resume.skills.all().delete()
# # #             for skill_data in data:
# # #                 Skill.objects.create(
# # #                     resume=resume,
# # #                     skill_name=skill_data.get('skill_name', ''),
# # #                     skill_type=skill_data.get('skill_type', 'technical'),
# # #                     proficiency_level=skill_data.get('proficiency_level', 0)
# # #                 )
# # #         elif section == 'work_experience':
# # #             # Clear existing work experiences and add new ones
# # #             resume.experiences.all().delete()
# # #             for exp_data in data:
# # #                 # Create the main experience entry
# # #                 experience = Experience.objects.create(
# # #                     resume=resume,
# # #                     company=exp_data.get('company', ''),
# # #                     position=exp_data.get('position', ''),
# # #                     location=exp_data.get('location', ''),
# # #                     start_date=exp_data.get('start_date', None),
# # #                     end_date=exp_data.get('end_date', None),
# # #                     is_current=exp_data.get('is_current', False)
# # #                 )
# # #
# # #                 # Add bullet points/responsibilities
# # #                 for bullet in exp_data.get('responsibilities', []):
# # #                     ExperienceBulletPoint.objects.create(
# # #                         experience=experience,
# # #                         description=bullet
# # #                     )
# # #         elif section == 'education':
# # #             # Clear existing education entries and add new ones
# # #             resume.educations.all().delete()
# # #             for edu_data in data:
# # #                 Education.objects.create(
# # #                     resume=resume,
# # #                     institution=edu_data.get('institution', ''),
# # #                     degree=edu_data.get('degree', ''),
# # #                     field_of_study=edu_data.get('field_of_study', ''),
# # #                     location=edu_data.get('location', ''),
# # #                     start_date=edu_data.get('start_date', None),
# # #                     end_date=edu_data.get('end_date', None),
# # #                     is_current=edu_data.get('is_current', False),
# # #                     gpa=edu_data.get('gpa', None),
# # #                     highlights=edu_data.get('highlights', '')
# # #                 )
# # #         elif section == 'projects':
# # #             # Clear existing projects and add new ones
# # #             resume.projects.all().delete()
# # #             for proj_data in data:
# # #                 # Create the main project entry
# # #                 project = Project.objects.create(
# # #                     resume=resume,
# # #                     title=proj_data.get('title', ''),
# # #                     description=proj_data.get('description', ''),
# # #                     url=proj_data.get('url', ''),
# # #                     start_date=proj_data.get('start_date', None),
# # #                     end_date=proj_data.get('end_date', None),
# # #                     is_current=proj_data.get('is_current', False)
# # #                 )
# # #
# # #                 # Add bullet points/highlights
# # #                 for bullet in proj_data.get('highlights', []):
# # #                     ProjectBulletPoint.objects.create(
# # #                         project=project,
# # #                         description=bullet
# # #                     )
# # #         elif section == 'certifications':
# # #             # Clear existing certifications and add new ones
# # #             resume.certifications.all().delete()
# # #             for cert_data in data:
# # #                 Certification.objects.create(
# # #                     resume=resume,
# # #                     name=cert_data.get('name', ''),
# # #                     issuing_organization=cert_data.get('issuing_organization', ''),
# # #                     issue_date=cert_data.get('issue_date', None),
# # #                     expiration_date=cert_data.get('expiration_date', None),
# # #                     credential_id=cert_data.get('credential_id', ''),
# # #                     credential_url=cert_data.get('credential_url', '')
# # #                 )
# # #         elif section == 'languages':
# # #             # Clear existing languages and add new ones
# # #             resume.languages.all().delete()
# # #             for lang_data in data:
# # #                 Language.objects.create(
# # #                     resume=resume,
# # #                     language=lang_data.get('language', ''),
# # #                     proficiency=lang_data.get('proficiency', 'basic')
# # #                 )
# # #         elif section == 'summary':
# # #             # Update the professional summary
# # #             resume.summary = data.get('summary', '')
# # #             resume.save()
# # #         elif section == 'contact_info':
# # #             # Update contact information
# # #             resume.email = data.get('email', resume.email)
# # #             resume.phone = data.get('phone', resume.phone)
# # #             resume.website = data.get('website', resume.website)
# # #             resume.linkedin = data.get('linkedin', resume.linkedin)
# # #             resume.github = data.get('github', resume.github)
# # #             resume.address = data.get('address', resume.address)
# # #             resume.city = data.get('city', resume.city)
# # #             resume.state = data.get('state', resume.state)
# # #             resume.zip_code = data.get('zip_code', resume.zip_code)
# # #             resume.country = data.get('country', resume.country)
# # #             resume.save()
# # #         elif section == 'additional_sections':
# # #             # Handle custom sections
# # #             resume.additional_sections.all().delete()
# # #             for section_data in data:
# # #                 custom_section = CustomData.objects.create(
# # #                     resume=resume,
# # #                     title=section_data.get('title', ''),
# # #                     order=section_data.get('order', 0)
# # #                 )
# # #
# # #                 # Add items to the custom section
# # #                 for item in section_data.get('items', []):
# # #                     CustomData.objects.create(
# # #                         section=custom_section,
# # #                         content=item
# # #                     )
# # #
# # #         return JsonResponse({'status': 'success'})
# # #     except Exception as e:
# # #         return JsonResponse({'status': 'error', 'message': str(e)})