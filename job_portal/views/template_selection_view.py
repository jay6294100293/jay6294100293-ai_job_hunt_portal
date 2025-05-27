# File: job_portal/views/template_selection_view.py
# Path: job_portal/views/template_selection_view.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from job_portal.models import Resume
from services.supporting_codes.resume_support_code import get_all_template_info, TEMPLATE_CHOICES


# MODIFIED: Import TEMPLATE_CHOICES from resume_support_code as well



class TemplateSelectionView(LoginRequiredMixin, View):
    template_html_name = 'resumes/template_select.html'

    def get(self, request, resume_id, *args, **kwargs):
        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        templates_information = get_all_template_info()
        next_step_url = reverse('job_portal:edit_resume_section',
                                kwargs={'resume_id': resume.id, 'section_slug': 'personal-info'})

        context = {
            'resume': resume,
            'current_template': resume.template_name,
            'templates_info': templates_information,
            'next_step_url': next_step_url,
            'page_title': _("Select a Template for '{resume_title}'").format(resume_title=resume.title),
        }
        return render(request, self.template_html_name, context)

    def post(self, request, resume_id, *args, **kwargs):
        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        selected_template_name = request.POST.get('template_name')

        if not selected_template_name:
            messages.error(request, _("No template was selected. Please choose a template."))
            templates_information = get_all_template_info()
            next_step_url = reverse('job_portal:edit_resume_section',
                                    kwargs={'resume_id': resume.id, 'section_slug': 'personal-info'})
            context = {
                'resume': resume,
                'current_template': resume.template_name,
                'templates_info': templates_information,
                'next_step_url': next_step_url,
                'page_title': _("Select a Template for '{resume_title}'").format(resume_title=resume.title),
            }
            return render(request, self.template_html_name, context)

        # MODIFIED: Validate against TEMPLATE_CHOICES imported from resume_support_code
        valid_templates = [choice[0] for choice in TEMPLATE_CHOICES]

        if selected_template_name in valid_templates:
            resume.template_name = selected_template_name
            resume.save()
            # Determine display name for the message
            display_name = selected_template_name
            for val, name in TEMPLATE_CHOICES:
                if val == selected_template_name:
                    display_name = name
                    break
            messages.success(request,
                             _("Template '{template_display_name}' selected for resume '{resume_title}'. You can now fill in the details.").format(
                                 template_display_name=display_name,
                                 resume_title=resume.title
                             )
                             )
            return redirect('job_portal:edit_resume_section', resume_id=resume.id, section_slug='personal-info')
        else:
            messages.error(request, _("Invalid template selected ('{selected_template}'). Please try again.").format(
                selected_template=selected_template_name))
            templates_information = get_all_template_info()
            next_step_url = reverse('job_portal:edit_resume_section',
                                    kwargs={'resume_id': resume.id, 'section_slug': 'personal-info'})
            context = {
                'resume': resume,
                'current_template': resume.template_name,
                'templates_info': templates_information,
                'next_step_url': next_step_url,
                'page_title': _("Select a Template for '{resume_title}'").format(resume_title=resume.title),
            }
            return render(request, self.template_html_name, context)