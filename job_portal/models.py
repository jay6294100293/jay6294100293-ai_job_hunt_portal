import os
import uuid

from django.utils import timezone

from django.db import models
from django.core.validators import FileExtensionValidator, MinLengthValidator
from auth_app.models import CustomUser

def resume_upload_path(instance, filename):
    """Generate a unique path for uploaded resume files."""
    # Generate a unique filename with original extension
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    # Return path like 'resumes/user_1/2023/03/filename.pdf'
    return os.path.join(
        'resumes',
        f"user_{instance.user.id}",
        str(timezone.now().year),
        str(timezone.now().month),
        filename
    )
class Resume(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('uploaded', 'Uploaded'),
        ('generated', 'Generated'),
        ('failed', 'Failed')
    ]

    first_name = models.CharField(max_length=100)
    mid_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=False)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    portfolio = models.URLField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True, validators=[MinLengthValidator(100)])

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='resumes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='uploaded')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.mid_name} {self.last_name}".strip()


class Skill(models.Model):
    SKILL_TYPES = [
        ('technical', 'Technical'),
        ('soft', 'Soft'),
        ('language', 'Language'),
        ('tool', 'Tool')
    ]

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
    skill_name = models.CharField(max_length=50)
    skill_type = models.CharField(max_length=20, choices=SKILL_TYPES, default='technical')
    proficiency_level = models.IntegerField(default=0)

    class Meta:
        ordering = ['skill_type', '-proficiency_level']

    def __str__(self):
        return self.skill_name


class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(max_length=100)
    employer = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.job_title} at {self.employer}"


class ExperienceBulletPoint(models.Model):
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE, related_name='bullet_points')
    description = models.TextField()
    keywords = models.ManyToManyField('Keyword', blank=True)

    def __str__(self):
        return f"Bullet Point for {self.experience.job_title}"


class Education(models.Model):
    DEGREE_TYPES = [
        ('high_school', 'High School'),
        ('associate', 'Associate Degree'),
        ('bachelor', "Bachelor's Degree"),
        ('master', "Master's Degree"),
        ('doctorate', 'Doctorate'),
        ('other', 'Other')
    ]

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='educations')
    school_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    degree_type = models.CharField(max_length=20, choices=DEGREE_TYPES, default='bachelor')
    field_of_study = models.CharField(max_length=100)
    graduation_date = models.DateField(blank=True, null=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ['-graduation_date']

    def __str__(self):
        return f"{self.degree} at {self.school_name}"


class Certification(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=100)
    institute = models.CharField(max_length=100, blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    expiration_date = models.DateField(blank=True, null=True)
    score = models.CharField(max_length=50, blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-completion_date']

    def __str__(self):
        return self.name


class Project(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='projects')
    project_name = models.CharField(max_length=100)
    summary = models.TextField(blank=True, null=True)
    technologies = models.ManyToManyField(Skill, blank=True)
    start_date = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    project_link = models.URLField(blank=True, null=True)
    github_link = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['-completion_date']

    def __str__(self):
        return self.project_name


class ProjectBulletPoint(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bullet_points')
    description = models.TextField()
    keywords = models.ManyToManyField('Keyword', blank=True)

    def __str__(self):
        return f"Bullet Point for {self.project.project_name}"


class Language(models.Model):
    PROFICIENCY_LEVELS = [
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('native', 'Native')
    ]

    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='languages')
    language_name = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS, default='basic')

    def __str__(self):
        return f"{self.language_name} ({self.proficiency})"


class CustomData(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='custom_data')
    name = models.CharField(max_length=100, help_text="Type of data (e.g., Achievements, Awards, Hobbies)")
    completion_date = models.DateField(blank=True, null=True)
    bullet_points = models.TextField(help_text="Add bullet points, one per line", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    institution_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-completion_date']

    def __str__(self):
        return self.name


class JobInput(models.Model):
    STATUS_CHOICES = [

        ('completed', 'Completed'),
        ('resume_created', 'Resume_Created'),
        ('resume_keyword_created', 'Resume_Keyword_Created'),
        ('failed', 'Failed'),
    ]

    AI_CHOICES = [
        ('chatgpt', 'ChatGPT'),
        ('gemini', 'Gemini'),
    ]

    company_name = models.CharField(max_length=100)
    job_post = models.CharField(max_length=100)
    job_description = models.TextField()
    job_post_url = models.URLField(blank=True, null=True)
    ai_choice = models.CharField(max_length=20, choices=AI_CHOICES, default='chatgpt')

    recruiter_name = models.CharField(max_length=100, blank=True, null=True)
    recruiter_email = models.EmailField(blank=True, null=True)
    recruiter_linkedin = models.URLField(blank=True, null=True)

    reference_name = models.CharField(max_length=100, blank=True, null=True)
    reference_email = models.EmailField(blank=True, null=True)
    reference_linkedin = models.URLField(blank=True, null=True)

    resume_file = models.FileField(
        upload_to=resume_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        blank=True,
        null=True
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Job Input"
        verbose_name_plural = "Job Inputs"

    def __str__(self):
        return f"{self.company_name} - {self.job_post}"


class Keyword(models.Model):
    KEYWORD_TYPES = [
        ('technical', 'Technical Skill'),
        ('soft', 'Soft Skill'),
        ('qualification', 'Qualification'),
        ('requirement', 'Requirement')
    ]

    job_input = models.ForeignKey(JobInput, on_delete=models.CASCADE, related_name='keywords')
    keyword = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=KEYWORD_TYPES, default='technical')
    relevance_score = models.FloatField(default=1.0)
    is_matched = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-relevance_score']

    def __str__(self):
        return f"{self.keyword} ({self.category})"


class AIProcessingLog(models.Model):
    job_input = models.ForeignKey(JobInput, on_delete=models.CASCADE, related_name='processing_logs')
    process_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.process_type} - {self.status}"


class APIUsage(models.Model):
    """
    Tracks API usage and costs for different AI services
    """
    API_CHOICES = [
        ('chatgpt', 'ChatGPT'),
        ('gemini', 'Gemini')
    ]

    OPERATION_TYPES = [
        ('keyword_extraction', 'Keyword Extraction'),
        ('resume_parsing', 'Resume Parsing'),
        ('content_generation', 'Content Generation'),
        ('analysis', 'Analysis')
    ]

    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('error', 'Error')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='api_usage')
    job_input = models.ForeignKey('JobInput', on_delete=models.CASCADE, related_name='api_usage', null=True)

    # API Details
    api_name = models.CharField(max_length=20, choices=API_CHOICES)
    operation = models.CharField(max_length=50, choices=OPERATION_TYPES)

    # Usage Metrics
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)

    # Performance Metrics
    response_time = models.FloatField(help_text="API response time in seconds", default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    error_message = models.TextField(blank=True, null=True)

    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    request_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'api_name', 'timestamp']),
            models.Index(fields=['api_name', 'operation']),
            models.Index(fields=['timestamp'])
        ]

    def __str__(self):
        return f"{self.api_name} - {self.operation} ({self.timestamp})"

    def calculate_cost(self):
        """Calculate cost based on tokens used"""
        COST_PER_TOKEN = {
            'chatgpt': {
                'input': 0.0000015,  # \$0.0015 per 1K tokens
                'output': 0.000002  # \$0.002 per 1K tokens
            },
            'gemini': {
                'input': 0.0000005,  # \$0.0005 per 1K tokens
                'output': 0.0000005  # $0.0005 per 1K tokens
            }
        }

        if self.api_name in COST_PER_TOKEN:
            costs = COST_PER_TOKEN[self.api_name]
            self.cost = (
                    (self.input_tokens * costs['input']) +
                    (self.output_tokens * costs['output'])
            )
            self.total_tokens = self.input_tokens + self.output_tokens
            self.save()

        return self.cost


