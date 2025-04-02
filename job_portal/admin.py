# job_portal/admin.py

from django.contrib import admin
from .models import (
    Resume, Skill, Experience, ExperienceBulletPoint,
    Education, Certification, Project, ProjectBulletPoint,
    Language, CustomData, JobInput, Keyword
)

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'created_at', 'status']
    list_filter = ['status', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']

@admin.register(JobInput)
class JobInputAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'job_post', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['company_name', 'job_post', 'user__email']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['skill_name', 'resume']
    search_fields = ['skill_name']

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['job_title', 'employer', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date']

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['school_name', 'degree', 'graduation_date']
    list_filter = ['graduation_date']

admin.site.register(ExperienceBulletPoint)
admin.site.register(Certification)
admin.site.register(Project)
admin.site.register(ProjectBulletPoint)
admin.site.register(Language)
admin.site.register(CustomData)
admin.site.register(Keyword)
