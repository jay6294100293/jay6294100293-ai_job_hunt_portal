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
