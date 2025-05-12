import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from auth_app.models import CustomUser


def resume_upload_path(instance, filename):
    """
    Generate a unique path for uploaded resume files.
    Handles files for Resume.source_uploaded_file, Resume.output_file,
    and potentially other models if they were to use it.
    """
    ext = filename.split('.')[-1].lower()
    filename = f"{uuid.uuid4()}.{ext}"

    user_id_path = "unknown_user"
    if hasattr(instance, 'user') and instance.user and hasattr(instance.user, 'id') and instance.user.id:
        user_id_path = f"user_{instance.user.id}"
    # If instance is Resume model directly
    elif isinstance(instance, Resume) and instance.user and hasattr(instance.user, 'id') and instance.user.id:
        user_id_path = f"user_{instance.user.id}"

    # Determine a base folder based on the instance type or field purpose if needed
    # For now, keeping it simple under 'resumes' and then user-specific folders.
    # You could add subfolders like 'source_uploads' vs 'generated_outputs' here if desired.
    base_folder = 'resumes'

    return os.path.join(
        base_folder,
        user_id_path,
        str(timezone.now().year),
        str(timezone.now().month),
        filename
    )


# --- ResumeManager ---
class ResumeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def published(self):
        return self.get_queryset().filter(publication_status=Resume.PUBLISHED)

    def drafts_for_user(self, user):
        return self.get_queryset().filter(user=user, publication_status=Resume.DRAFT).order_by('-updated_at')


# --- Resume Model (Final Version) ---
class Resume(models.Model):
    # Status reflecting the origin or primary nature of the resume data/file
    STATUS_CHOICES = [
        ('created', 'Created from Scratch'),  # Built via wizard
        ('uploaded', 'Populated from Upload'),  # Created by parsing an uploaded file
        ('generated', 'AI-Generated Tailored'),  # Created by AI based on a job and another resume
        ('failed', 'Processing Failed')  # If any of the above failed
    ]

    # Publication Status reflecting user's intent for visibility/completion
    DRAFT = 'DRAFT'
    PUBLISHED = 'PUBLISHED'
    ARCHIVED = 'ARCHIVED'
    PUBLICATION_STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
        (ARCHIVED, 'Archived'),
    ]

    # Visibility choices for resume sharing
    VISIBILITY_PRIVATE = 'PRIVATE'
    VISIBILITY_UNLISTED = 'UNLISTED'
    VISIBILITY_PUBLIC = 'PUBLIC'
    VISIBILITY_CHOICES = [
        (VISIBILITY_PRIVATE, 'Private (Only you)'),
        (VISIBILITY_UNLISTED, 'Unlisted (Shareable with link)'),
        (VISIBILITY_PUBLIC, 'Public'),  # Requires more logic for actual public pages
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')

    title = models.CharField(max_length=255, default='Untitled Resume',
                             help_text="User-defined name for this resume version.")
    slug = models.SlugField(max_length=255, unique=True, blank=True,
                            help_text="URL-friendly identifier, auto-generated.")

    # Personal Information fields (populated by wizard or parsed from upload)
    first_name = models.CharField(max_length=100, blank=True)
    mid_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=False,
                              blank=True)  # Not unique per Resume, but user's email in CustomUser is unique
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True, max_length=255)
    github = models.URLField(blank=True, null=True, max_length=255)
    portfolio = models.URLField(blank=True, null=True, max_length=255)
    summary = models.TextField(blank=True, null=True, validators=[MinLengthValidator(100)])

    # Existing 'status' field, now clearly for origin/type
    # Default 'created' for wizard. Views for upload/AI generation will set this accordingly.
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='created',
        help_text="Origin or type of this resume content."
    )

    # New 'publication_status' for draft/publish workflow
    publication_status = models.CharField(
        max_length=10,
        choices=PUBLICATION_STATUS_CHOICES,
        default=DRAFT,
        help_text="Current stage in the creation/review process."
    )

    template_name = models.CharField(max_length=100, blank=True, null=True,
                                     help_text="Visual template selected for this resume.")
    is_primary = models.BooleanField(default=False, help_text="Is this the user's primary resume?")
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_PRIVATE,
        help_text="Sharing visibility of this resume."
    )

    # --- NEW: Field for the originally uploaded file (if applicable) ---
    source_uploaded_file = models.FileField(
        upload_to=resume_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'txt'])],
        blank=True, null=True,
        help_text="The original file uploaded by the user, if this resume was created from an upload."
    )

    # --- Field for the system-generated output (e.g., PDF/DOCX from wizard data + template) ---
    output_file = models.FileField(
        upload_to=resume_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])],
        blank=True, null=True,
        help_text="The system-generated formatted file (e.g., PDF) for this resume version."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ResumeManager()  # Custom manager

    class Meta:
        ordering = ['-is_primary', '-updated_at']
        verbose_name = "Resume (Wizard/Uploaded/Generated)"
        verbose_name_plural = "Resumes (Wizard/Uploaded/Generated)"

    def __str__(self):
        display_title = self.title if self.title and self.title != 'Untitled Resume' else self.full_name
        if not display_title:
            display_title = f"Resume ID {self.pk}"
        primary_indicator = " (Primary)" if self.is_primary else ""
        pub_status_display = self.get_publication_status_display() if self.publication_status else "N/A"
        user_display = self.user.username if self.user else "N/A"
        return f"{display_title}{primary_indicator} ({pub_status_display}, {self.get_status_display()}) by {user_display}"

    @property
    def full_name(self):
        parts = [self.first_name, self.mid_name, self.last_name]
        return " ".join(filter(None, parts)).strip()

    def _generate_slug(self):
        # Simplified slug generation for brevity. Ensure it's robust for your needs.
        user_id_part = str(self.user_id).replace('-', '')[:8] if self.user_id else 'nouser'
        base_value = self.title if self.title and self.title != 'Untitled Resume' else self.full_name
        if not base_value:
            base_value = f"resume-{user_id_part}-{uuid.uuid4().hex[:4]}"

        temp_slug = slugify(f"{base_value}-{user_id_part}")  # Add user_id to base for better initial uniqueness
        if not temp_slug:  # if slugify results in empty string
            temp_slug = f"resume-{user_id_part}-{uuid.uuid4().hex[:6]}"

        # Ensure uniqueness globally for the slug
        slug = temp_slug
        counter = 1
        qs = Resume.objects.filter(slug=slug)
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        while qs.exists():
            slug = f"{temp_slug}-{counter}"
            counter += 1
            qs = Resume.objects.filter(slug=slug)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_slug()

        if self.is_primary:
            Resume.objects.filter(user=self.user, is_primary=True).exclude(pk=self.pk).update(is_primary=False)

        super().save(*args, **kwargs)

class Skill(models.Model):
    # More general skill categories, including an 'OTHER' option
    SKILL_CATEGORY_CHOICES = [
        ('CORE_COMPETENCY', 'Core Competency / Professional'),  # e.g., Project Management, Research
        ('TECHNICAL_DIGITAL', 'Technical / Digital / IT'),  # e.g., Python, SEO, Cloud Computing
        ('INTERPERSONAL', 'Interpersonal / Soft Skill'),  # e.g., Communication, Teamwork
        ('TOOLS_SOFTWARE', 'Tools / Software Proficiency'),  # e.g., MS Excel, Adobe Photoshop, Jira
        # ('LANGUAGE_PROFICIENCY', 'Language Proficiency'), # Kept commented as you have a dedicated Language model
        # Could be added back if you want skill-like language entries here too.
        ('OTHER', 'Other (Please specify)')  # For user-defined categories
    ]

    resume = models.ForeignKey('Resume', on_delete=models.CASCADE,
                               related_name='skills')  # Use string if Resume defined later
    skill_name = models.CharField(
        max_length=100,  # Increased max_length from your 50 for more descriptive skill names
        help_text="Name of the skill, e.g., Strategic Planning, Python, Public Speaking."
    )

    # Stores the choice from SKILL_CATEGORY_CHOICES
    skill_category_choice = models.CharField(
        max_length=30,  # Max length of your choice keys (e.g., 'CORE_COMPETENCY')
        choices=SKILL_CATEGORY_CHOICES,
        # default='CORE_COMPETENCY', # Or perhaps make it blank if you want user to always choose
        blank=True,  # Making it blank=True so user can choose to leave it uncategorized or pick other
        null=True,  # If blank is true, null is often also true for CharFields with choices
        help_text="Select a predefined category for the skill."
    )

    # Field for user-defined category if 'OTHER' is selected in skill_category_choice
    skill_category_other = models.CharField(
        max_length=100,
        blank=True,
        null=True,  # Can be null if not used
        help_text="If 'Other' category is selected above, specify your category here."
    )

    # Your existing proficiency_level field
    proficiency_level = models.IntegerField(
        default=0,  # Represents a scale, e.g., 0 (not set/basic) to 5 (expert) or 0-100.
        # The UI will determine how this is presented and input.
        help_text="Proficiency level (e.g., on a scale of 1-5, where 0 might mean 'not specified')."
    )

    # --- NEW: Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['skill_category_choice', 'skill_category_other', '-proficiency_level', 'skill_name']
        unique_together = [['resume', 'skill_name']]
        # This means "Python" can only appear once per resume regardless of category.
        # If "Python" (Technical) should be different from "Python (Teaching)" (Other: "Pedagogical Skill"),
        # you might need a more complex uniqueness validation in the clean() method, as
        # unique_together with nullable fields like skill_category_other can be tricky at DB level.
        # For most cases, skill_name being unique per resume is a good starting point.

    def __str__(self):
        category_display = self.effective_skill_category  # Use the property
        level_display = f" (Level: {self.proficiency_level})" if self.proficiency_level else ""  # Optionally show level
        return f"{self.skill_name}{level_display} [{category_display}] for Resume ID: {self.resume_id}"

    def clean(self):
        super().clean()  # Call parent's clean method

        # If 'OTHER' is chosen for category_choice, then 'skill_category_other' must be filled.
        if self.skill_category_choice == 'OTHER':
            if not self.skill_category_other or self.skill_category_other.strip() == "":
                raise ValidationError(
                    {
                        'skill_category_other': "Please specify your category if 'Other' is selected for the category choice."}
                )
        # If a predefined category (not 'OTHER') is chosen, then 'skill_category_other' should be blank.
        elif self.skill_category_other and self.skill_category_other.strip() != "":
            # Optionally, you could auto-clear it:
            # self.skill_category_other = None
            # Or raise a validation error if you want the user to explicitly clear it:
            raise ValidationError(
                {
                    'skill_category_other': "Custom category should only be specified if 'Other' is selected as the category choice."}
            )

        # Ensure category choice is made if skill_category_other is filled (edge case)
        if self.skill_category_other and not self.skill_category_choice:
            raise ValidationError(
                {
                    'skill_category_choice': "Please select a category choice, or 'Other' if specifying a custom category."}
            )

    @property
    def effective_skill_category(self):
        """Returns the actual category name, whether from choices or custom input."""
        if self.skill_category_choice == 'OTHER' and self.skill_category_other and self.skill_category_other.strip():
            return self.skill_category_other.strip()
        elif self.skill_category_choice:
            return self.get_skill_category_choice_display()
        return "Uncategorized"  # Fallback if no category info is present


class Experience(models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(
        max_length=100,
        help_text="Your role or title, e.g., Software Engineer, Project Manager."
    )
    employer = models.CharField(
        max_length=100,
        help_text="Name of the company or organization."
    ) # Using 'employer' as per your model
    location = models.CharField(
        max_length=100,
        blank=True, null=True, # MODIFIED: Made optional
        help_text="City and state/country, e.g., San Francisco, CA. Can be 'Remote'."
    )
    start_date = models.DateField(
        help_text="When you started this role."
    ) # Kept as non-nullable as per your model
    end_date = models.DateField(
        blank=True, null=True,
        help_text="When you ended this role (leave blank if current)."
    )
    is_current = models.BooleanField(
        default=False,
        help_text="Check this if this is your current role."
    )

    # --- NEW: Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_current', '-start_date'] # MODIFIED: Prioritize current jobs

    def __str__(self):
        current_status = " (Current)" if self.is_current else ""
        return f"{self.job_title} at {self.employer}{current_status} (Resume: {self.resume_id})"

    def save(self, *args, **kwargs):
        # Ensure end_date is cleared if is_current is True
        if self.is_current and self.end_date is not None:
            self.end_date = None
        super().save(*args, **kwargs)


class ExperienceBulletPoint(models.Model):
    experience = models.ForeignKey(
        'Experience',
        on_delete=models.CASCADE,
        related_name='bullet_points',
        help_text="The work experience this bullet point describes."
    )
    description = models.TextField(
        help_text="Describe a specific achievement or responsibility for this experience, ideally starting with an action verb."
    )
    # keywords = models.ManyToManyField('Keyword', blank=True) # --- REMOVED as per our discussion ---

    # --- NEW: Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']  # Order bullet points by creation time by default for a given experience
        # verbose_name = "Experience Detail" # Optional: for admin display
        # verbose_name_plural = "Experience Details"

    def __str__(self):
        # Ensure experience and job_title exist before trying to access them for robustness
        experience_job_title = "Unknown Experience"
        if self.experience and hasattr(self.experience, 'job_title') and self.experience.job_title:
            experience_job_title = self.experience.job_title

        # Truncate description for a cleaner display in lists or the admin
        desc_snippet = (self.description[:47] + '...') if len(self.description) > 50 else self.description
        return f"Bullet for '{experience_job_title}': \"{desc_snippet}\""


class Education(models.Model):
    DEGREE_TYPES = [
        ('high_school', 'High School Diploma/GED'),
        ('associate', 'Associate Degree'),
        ('bachelor', "Bachelor's Degree"),
        ('master', "Master's Degree"),
        ('doctorate', 'Doctorate Degree'),
        ('professional', 'Professional Degree (e.g., MD, JD, DDS)'),
        ('diploma', 'Diploma (Formal Program)'),
        ('coursework', 'Significant Coursework/Study (e.g., Bootcamp, Exchange Program)'),
        ('other', 'Other Formal Qualification')  # User specifies the exact name in 'degree_name'
    ]

    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, related_name='educations')
    school_name = models.CharField(
        max_length=100,
        help_text="Name of the institution (e.g., University of Example, Online Bootcamp Name)."
    )
    location = models.CharField(
        max_length=100,
        blank=True, null=True,  # MODIFIED: Made optional
        help_text="City, State/Country (e.g., New York, NY). Optional for online."
    )

    # RENAMED from 'degree' to 'degree_name' and made primary descriptor
    degree_name = models.CharField(
        max_length=150,  # Slightly increased length for descriptive names
        help_text="Specific title of your degree, diploma, or qualification (e.g., B.S. in Computer Science, Advanced Pastry Diploma, Full-Stack Web Development Bootcamp)."
    )

    degree_type = models.CharField(
        max_length=20,
        choices=DEGREE_TYPES,
        blank=True, null=True,  # MODIFIED: Made optional, default removed
        help_text="Select the general type of this educational qualification."
    )

    field_of_study = models.CharField(
        max_length=100,
        blank=True, null=True,  # MODIFIED: Made optional
        help_text="Your major or primary area of study (e.g., Computer Science, Marketing). Not always applicable."
    )
    graduation_date = models.DateField(
        blank=True, null=True,
        help_text="Month and year of graduation or expected completion. You can select the first day of the month if only month/year is known."
    )
    gpa = models.DecimalField(
        max_digits=4,  # MODIFIED: Increased max_digits (e.g., 3.75, 4.00)
        decimal_places=2,
        blank=True, null=True,
        help_text="Your Grade Point Average, if applicable (e.g., 3.85). Optional."
    )

    # --- NEW SUGGESTION: Optional description field ---
    description = models.TextField(
        blank=True, null=True,
        help_text="Optional: Add details like honors, relevant coursework, thesis, or other notable achievements related to this education."
    )

    # --- NEW: Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-graduation_date', '-created_at']  # MODIFIED: Added secondary sort
        verbose_name = "Education Entry"
        verbose_name_plural = "Education Entries"

    def __str__(self):
        grad_info = ""
        if self.graduation_date:
            current_date = timezone.now().date()
            if self.graduation_date > current_date:
                grad_info = f" (Expected: {self.graduation_date.strftime('%b %Y')})"
            else:
                grad_info = f" (Graduated: {self.graduation_date.strftime('%b %Y')})"
        else:
            # Could check start_date to infer if it's ongoing or if dates are just not provided
            grad_info = " (Date TBD or Ongoing)"

        return f"{self.degree_name} from {self.school_name}{grad_info}"

class Certification(models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(
        max_length=150, # Increased max_length slightly
        help_text="Name of the certification, license, or course, e.g., Certified Scrum Master, AWS Certified Solutions Architect."
    )
    # SUGGESTION: Renamed 'institute' to 'issuing_organization' for standard resume terminology
    issuing_organization = models.CharField(
        max_length=100,
        blank=True, null=True,
        help_text="The organization that issued the certification, e.g., Scrum Alliance, Amazon Web Services."
    )
    # SUGGESTION: Renamed 'completion_date' to 'issue_date'
    issue_date = models.DateField(
        blank=True, null=True,
        help_text="The date the certification was issued or completed. Select the first day of the month if only month/year is known."
    )
    expiration_date = models.DateField(
        blank=True, null=True,
        help_text="If applicable, the date the certification expires. Leave blank if it does not expire."
    )
    # --- SUGGESTION: New field for Credential ID ---
    credential_id = models.CharField(
        max_length=100,
        blank=True, null=True,
        help_text="Any ID or number associated with the credential for verification (optional)."
    )
    score = models.CharField( # Your existing field
        max_length=50,
        blank=True, null=True,
        help_text="Your score or grade, if applicable and you wish to include it."
    )
    link = models.URLField( # Your existing field, added max_length
        max_length=255,
        blank=True, null=True,
        help_text="A URL to the certificate, transcript, or verification page (optional)."
    )
    description = models.TextField( # Your existing field
        blank=True, null=True,
        help_text="Optional: Any additional relevant details about the certification or what you learned."
    )

    # --- NEW: Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', 'name'] # MODIFIED: Using 'issue_date' and added 'name'
        verbose_name = "Certification / License"
        verbose_name_plural = "Certifications & Licenses"

    def __str__(self):
        org_display = f" from {self.issuing_organization}" if self.issuing_organization else ""
        date_display = f" (Issued: {self.issue_date.strftime('%b %Y')})" if self.issue_date else ""
        return f"{self.name}{org_display}{date_display}"


class Project(models.Model):
    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, related_name='projects')
    project_name = models.CharField(
        max_length=150,  # Increased max_length slightly
        help_text="The title or name of your project."
    )
    summary = models.TextField(  # Your project description field
        blank=True, null=True,
        help_text="A brief overview of the project, its purpose, your role, and key achievements."
    )
    technologies = models.ManyToManyField(
        'Skill',
        blank=True,
        related_name="projects_showcasing",  # Descriptive reverse relation from Skill
        help_text="Select or add skills/technologies used in this project."
    )
    start_date = models.DateField(
        blank=True, null=True,
        help_text="The start date of the project (optional)."
    )
    completion_date = models.DateField(  # Your field name is 'completion_date'
        blank=True, null=True,
        help_text="The completion date of the project (optional, leave blank if ongoing or not applicable)."
    )
    project_link = models.URLField(
        max_length=255,  # ADDED max_length
        blank=True, null=True,
        help_text="A URL to the live project, demo, or further information, if available."
    )
    github_link = models.URLField(
        max_length=255,  # ADDED max_length
        blank=True, null=True,
        help_text="A URL to the project's source code repository (e.g., GitHub), if applicable."
    )

    # --- NEW: Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-completion_date', 'project_name']  # Kept your primary sort, added project_name
        verbose_name = "Project Entry"
        verbose_name_plural = "Project Entries"

    def __str__(self):
        date_info = ""
        # Check if timezone.now() is available, else use datetime.date.today() as a fallback
        # For model methods, it's better if now() is passed or handled carefully to avoid naive/aware issues
        # but for a simple __str__ this is generally okay if settings.USE_TZ=True.
        # For robustness, will simply format dates if they exist.

        current_year = timezone.now().year  # For comparing if completion date is in future

        if self.completion_date:
            if self.start_date and self.completion_date < self.start_date:
                date_info = f" (Dates Need Review)"
            elif self.completion_date.year > current_year:  # Simple check for future
                date_info = f" (Expected Completion: {self.completion_date.strftime('%b %Y')})"
            else:
                date_info = f" (Completed: {self.completion_date.strftime('%b %Y')})"
        elif self.start_date:
            if self.start_date.year > current_year and self.start_date.month > timezone.now().month:  # Simple check for future start
                date_info = f" (Starting: {self.start_date.strftime('%b %Y')})"
            else:
                date_info = f" (Ongoing since: {self.start_date.strftime('%b %Y')})"

        return f"{self.project_name}{date_info}"


class ProjectBulletPoint(models.Model):
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        related_name='bullet_points',
        help_text="The project this bullet point describes."
    )
    description = models.TextField(
        help_text="Describe a specific feature, accomplishment, or contribution for this project, ideally highlighting impact or skills used."
    )
    # keywords = models.ManyToManyField('Keyword', blank=True) # --- REMOVED as per our discussion ---

    # --- NEW: Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']  # Order bullet points by creation time by default for a given project
        verbose_name = "Project Detail/Bullet Point"
        verbose_name_plural = "Project Details/Bullet Points"

    def __str__(self):
        # Ensure project and project_name exist before trying to access them for robustness
        project_name_display = "Unknown Project"
        if self.project and hasattr(self.project, 'project_name') and self.project.project_name:
            project_name_display = self.project.project_name

        # Truncate description for a cleaner display in lists or the admin
        desc_snippet = (self.description[:47] + '...') if len(self.description) > 50 else self.description
        return f"For '{project_name_display}': \"{desc_snippet}\""


class Language(models.Model):
    PROFICIENCY_LEVELS = [
        ('ELEMENTARY', 'Elementary Proficiency'),        # Common framework term
        ('LIMITED_WORKING', 'Limited Working Proficiency'), # Common framework term
        ('PROFESSIONAL_WORKING', 'Professional Working Proficiency'), # Common framework term
        ('FULL_PROFESSIONAL', 'Full Professional Proficiency'),   # Common framework term
        ('NATIVE_OR_BILINGUAL', 'Native or Bilingual Proficiency') # Common framework term
    ]

    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, related_name='languages')
    language_name = models.CharField(
        max_length=100,
        help_text="The language you speak, e.g., Spanish, French, Mandarin."
    )
    proficiency = models.CharField(
        max_length=30, # Adjusted to fit longer choice keys like 'PROFESSIONAL_WORKING'
        choices=PROFICIENCY_LEVELS,
        default='PROFESSIONAL_WORKING', # Changed default to a common mid-tier
        help_text="Your proficiency level in this language."
    )

    # --- NEW: Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['language_name']
        unique_together = [['resume', 'language_name']] # Prevent duplicate languages for the same resume
        verbose_name = "Language Proficiency"
        verbose_name_plural = "Language Proficiencies"

    def __str__(self):
        return f"{self.language_name} ({self.get_proficiency_display()}) - Resume: {self.resume_id}"


class CustomData(models.Model): # This model represents a Custom Section
    resume = models.ForeignKey(
        'Resume',
        on_delete=models.CASCADE,
        related_name='custom_sections', # MODIFIED: related_name for clarity
        help_text="The resume this custom section belongs to."
    )
    # 'name' field acts as the title of the custom section
    name = models.CharField(
        max_length=150, # Increased max_length
        help_text="Title for this custom section (e.g., Achievements, Awards, Publications, Volunteer Experience)."
    )
    # 'institution_name' for context like awarding body, organization for volunteering, etc.
    institution_name = models.CharField(
        max_length=100,
        blank=True, null=True,
        help_text="Name of the associated institution or organization, if applicable (e.g., for an award or volunteer role)."
    )
    # 'completion_date' or a general 'relevant_date' for the section or its items
    completion_date = models.DateField(
        blank=True, null=True,
        help_text="A relevant date for this section or its content (e.g., date of award, project completion, membership period). Optional."
    )
    # 'description' for an optional overview of the custom section
    description = models.TextField(
        blank=True, null=True,
        help_text="An optional paragraph describing this section or its contents."
    )
    # 'bullet_points' as a block of text, one point per line
    bullet_points = models.TextField(
        help_text="List key details or achievements as bullet points, one per line.",
        blank=True, null=True
    )
    link = models.URLField(
        max_length=255, # ADDED max_length
        blank=True, null=True,
        help_text="An optional URL related to this section (e.g., link to publication, award page)."
    )

    # --- NEW: Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # --- SUGGESTION: Field for manual ordering by user ---
    # order = models.PositiveIntegerField(default=0, blank=False, null=False, help_text="Order in which to display this section.")

    class Meta:
        ordering = ['-completion_date', 'name'] # MODIFIED: Kept your primary, added 'name'
        # If 'order' field is added: ordering = ['order', '-completion_date', 'name']
        verbose_name = "Custom Resume Section"
        verbose_name_plural = "Custom Resume Sections"

    def __str__(self):
        date_str = f" ({self.completion_date.strftime('%b %Y')})" if self.completion_date else ""
        return f"{self.name}{date_str} for Resume: {self.resume_id}"


class JobInput(models.Model):
    # Choices reflect stages of processing for this job input
    STATUS_CHOICES = [
        ('pending_selection', 'Pending Resume Selection'),  # If source_resume can be initially null
        ('pending_processing', 'Pending AI Processing'),  # After resume is selected
        ('processing', 'AI Processing Underway'),
        ('completed', 'Materials Generated'),  # Successfully generated materials
        ('failed_processing', 'AI Processing Failed'),  # AI step failed
        # Your existing choices, re-evaluate if they fit the new flow or are sub-statuses of 'completed'
        # ('resume_created', 'Resume_Created'), # This might now refer to AI tailoring creating a *new* Resume instance
        # ('resume_keyword_created', 'Resume_Keyword_Created'),
    ]

    AI_CHOICES = [  # From your model
        ('chatgpt', 'ChatGPT'),
        ('gemini', 'Gemini'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_inputs'  # ADDED related_name
    )

    # --- NEW: Link to a wizard-built or uploaded/parsed Resume object ---
    source_resume = models.ForeignKey(
        'Resume',
        on_delete=models.SET_NULL,  # Keep JobInput if Resume is deleted, but link is lost
        null=True,  # User might create JobInput then select Resume, or it must be selected upfront via form
        blank=True,  # Allow blank in forms if selection is a subsequent step
        related_name='used_in_job_inputs',
        help_text="The user's resume selected as the base for generating application materials."
    )

    # --- REMOVED: resume_file field ---
    # resume_file = models.FileField(
    #     upload_to=resume_upload_path,
    #     validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
    #     blank=True,
    #     null=True
    # )

    # Job Details
    company_name = models.CharField(max_length=100, help_text="Name of the company.")
    job_post = models.CharField(max_length=100,
                                help_text="The title of the job you are applying for.")  # Your field, often job_title
    job_description = models.TextField(help_text="The full job description text.")
    job_post_url = models.URLField(blank=True, null=True, max_length=2083,
                                   help_text="URL to the job posting (optional).")  # Increased max_length

    # AI Configuration
    ai_choice = models.CharField(max_length=20, choices=AI_CHOICES, default='chatgpt',
                                 help_text="AI model to use for generation.")

    # Optional Recruiter Info
    recruiter_name = models.CharField(max_length=100, blank=True, null=True)
    recruiter_email = models.EmailField(blank=True, null=True)
    recruiter_linkedin = models.URLField(blank=True, null=True, max_length=2083)  # Increased max_length

    # Optional Reference Info
    reference_name = models.CharField(max_length=100, blank=True, null=True)
    reference_email = models.EmailField(blank=True, null=True)
    reference_linkedin = models.URLField(blank=True, null=True, max_length=2083)  # Increased max_length

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='pending_selection',  # Changed default to reflect initial state
        help_text="Current processing status of this job input."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # From your model
        verbose_name = "Job Application Input"  # Slightly more descriptive
        verbose_name_plural = "Job Application Inputs"

    def __str__(self):
        resume_title = self.source_resume.title if self.source_resume else "No Resume Selected"
        return f"Input for {self.job_post} at {self.company_name} (Using: {resume_title})"


class Keyword(models.Model):
    KEYWORD_TYPES = [
        ('technical', 'Technical Skill'),
        ('soft', 'Soft Skill'),
        ('qualification', 'Qualification'), # e.g., "Master's Degree", "PMP Certification"
        ('experience_years', 'Years of Experience'), # e.g., "5+ years Java"
        ('industry_knowledge', 'Industry Knowledge'), # e.g., "FinTech", "Healthcare IT"
        ('responsibility', 'Key Responsibility'), # Phrases from job duties
        ('requirement', 'General Requirement') # Other stated requirements
    ]

    job_input = models.ForeignKey(
        'JobInput',
        on_delete=models.CASCADE,
        related_name='extracted_keywords', # MODIFIED: more specific related_name
        help_text="The job input from which this keyword was extracted."
    )
    keyword = models.CharField(
        max_length=150, # Increased max_length slightly
        help_text="The extracted keyword or keyphrase from the job description."
    )
    category = models.CharField(
        max_length=30, # Adjusted for potentially longer keys like 'industry_knowledge'
        choices=KEYWORD_TYPES,
        default='technical',
        help_text="The category of the extracted keyword."
    )
    relevance_score = models.FloatField(
        default=1.0,
        # validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], # Optional: if score is normalized between 0 and 1
        help_text="A score indicating the relevance or importance of this keyword (e.g., based on frequency, position). Higher is more relevant."
    )
    # 'is_matched' indicates if this keyword (from the job description) was found/covered in the user's resume
    is_matched = models.BooleanField(
        default=False,
        help_text="Whether this keyword from the job description is considered matched/covered by the user's resume."
    )

    # --- NEW: Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True) # You already had this
    updated_at = models.DateTimeField(auto_now=True)   # ADDED for consistency

    class Meta:
        ordering = ['-relevance_score', 'keyword'] # MODIFIED: Added 'keyword' as secondary sort
        unique_together = [['job_input', 'keyword', 'category']] # SUGGESTION: Prevents duplicate keyword entries for the same job and category
        verbose_name = "Extracted Job Keyword"
        verbose_name_plural = "Extracted Job Keywords"

    def __str__(self):
        # Ensure job_input and its relevant fields exist for robustness
        job_input_info = f"for Job Input {self.job_input_id}" if self.job_input_id else "for Unknown Job Input"
        return f"'{self.keyword}' ({self.get_category_display()}) {job_input_info}"


class AIProcessingLog(models.Model):
    # --- SUGGESTION: Define choices for process_type for consistency ---
    PROCESS_TYPE_CHOICES = [
        ('keyword_extraction', 'Keyword Extraction'),
        ('resume_analysis', 'Resume Analysis'),
        ('resume_tailoring', 'Resume Tailoring'),
        ('cover_letter_generation', 'Cover Letter Generation'),
        ('linkedin_message_generation', 'LinkedIn Message Generation'),
        ('email_template_generation', 'Email Template Generation'),
        ('bullet_point_enhancement', 'Bullet Point Enhancement'),
        ('summary_generation', 'Summary Generation'),
        ('unknown', 'Unknown Process'),
    ]

    # --- SUGGESTION: Define choices for status for consistency ---
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('started', 'Started'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('partial_success', 'Partial Success'),  # If some parts succeeded, others failed
        ('retrying', 'Retrying'),
    ]

    job_input = models.ForeignKey(
        'JobInput',
        on_delete=models.CASCADE,
        related_name='processing_logs',
        help_text="The specific job input this log entry pertains to."
    )
    process_type = models.CharField(
        max_length=50,
        choices=PROCESS_TYPE_CHOICES,  # Using suggested choices
        default='unknown',
        help_text="Type of AI processing performed (e.g., keyword extraction, resume tailoring)."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,  # Using suggested choices
        default='pending',
        help_text="Current status of this processing step."
    )
    error_message = models.TextField(
        blank=True, null=True,
        help_text="Details of any error that occurred during processing."
    )

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text="Timestamp when this processing step was initiated or logged.")  # You had this
    updated_at = models.DateTimeField(auto_now=True,
                                      help_text="Timestamp when this log entry was last updated.")  # ADDED
    completed_at = models.DateTimeField(
        blank=True, null=True,
        help_text="Timestamp when this processing step was completed (successfully or failed)."
    )  # You had this

    class Meta:
        ordering = ['-created_at']  # Your existing ordering is good
        verbose_name = "AI Processing Log Entry"
        verbose_name_plural = "AI Processing Log Entries"

    def __str__(self):
        job_input_display = f"JobInput {self.job_input_id}" if self.job_input_id else "Unknown JobInput"
        # Use get_..._display() for fields with choices
        process_type_display = self.get_process_type_display() if self.process_type else self.process_type
        status_display = self.get_status_display() if self.status else self.status
        return f"Log for {job_input_display}: {process_type_display} - {status_display} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class APIUsage(models.Model):
    """
    Tracks API usage, token counts, and costs for different AI services.
    """
    API_CHOICES = [
        ('chatgpt', 'ChatGPT'),
        ('gemini', 'Gemini'),
        ('unknown_api', 'Unknown API')  # Fallback
    ]

    OPERATION_TYPES = [
        ('keyword_extraction', 'Keyword Extraction'),
        ('resume_parsing', 'Resume Parsing'),
        ('resume_tailoring', 'Resume Tailoring'),  # Added
        ('cover_letter_generation', 'Cover Letter Generation'),  # Added
        ('linkedin_message_generation', 'LinkedIn Message Generation'),  # Added
        ('email_template_generation', 'Email Template Generation'),  # Added
        ('bullet_point_enhancement', 'Bullet Point Enhancement'),  # Added
        ('summary_generation', 'Summary Generation'),  # Added
        ('content_generation', 'Generic Content Generation'),  # More general than 'content_generation'
        ('analysis', 'General Analysis'),  # More general
        ('other_operation', 'Other Operation'),  # Fallback
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),  # Request initiated, awaiting response
        ('success', 'Success'),  # API call successful
        ('failed', 'Failed'),  # API call failed (e.g., network issue, API error)
        ('error', 'Application Error')  # Error in our application logic before/after API call
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # Keep log if user is deleted, but link to user
        null=True, blank=True,  # Might have system-level API calls not tied to a specific user
        related_name='api_usage_logs',  # More specific related_name
        help_text="The user who initiated the action leading to this API call, if applicable."
    )
    # Link to JobInput if this usage is for materials related to a specific job application
    job_input = models.ForeignKey(
        'JobInput',
        on_delete=models.SET_NULL,  # Keep log if JobInput is deleted
        null=True, blank=True,
        related_name='api_usage_logs',
        help_text="The job input context for this API call, if applicable."
    )
    # --- SUGGESTION: Link to Resume if usage is directly for enhancing/analyzing a resume ---
    resume = models.ForeignKey(
        'Resume',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='api_usage_logs',
        help_text="The resume context for this API call, if not tied to a specific JobInput (e.g., direct resume enhancement)."
    )

    # API Details
    api_name = models.CharField(
        max_length=20,
        choices=API_CHOICES,
        default='unknown_api',
        help_text="Name of the AI service used."
    )
    operation = models.CharField(
        max_length=50,
        choices=OPERATION_TYPES,
        default='other_operation',
        help_text="Specific type of operation performed using the API."
    )

    # Usage Metrics
    input_tokens = models.IntegerField(default=0, null=True, blank=True, help_text="Number of tokens sent to the API.")
    output_tokens = models.IntegerField(default=0, null=True, blank=True,
                                        help_text="Number of tokens received from the API.")
    total_tokens = models.IntegerField(default=0, null=True, blank=True,
                                       help_text="Total tokens processed (input + output). Auto-calculated.")
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0.000000,
                               help_text="Calculated cost for this API call. Auto-calculated.")

    # Performance Metrics
    response_time_ms = models.PositiveIntegerField(  # Changed to PositiveIntegerField for milliseconds
        null=True, blank=True,
        help_text="API response time in milliseconds."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',  # Default to pending until success/failure is recorded
        help_text="Status of the API call."
    )
    error_message = models.TextField(
        blank=True, null=True,
        help_text="Any error message returned by the API or an internal error."
    )

    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True,
                                     help_text="When the API call log entry was created.")  # Renamed from created_at for clarity
    updated_at = models.DateTimeField(auto_now=True, help_text="When the log entry was last updated.")  # NEW
    request_id = models.CharField(max_length=100, blank=True, null=True, db_index=True,
                                  help_text="Unique ID for the API request, if provided by the API.")

    class Meta:
        ordering = ['-timestamp']  # Your existing ordering
        verbose_name = "API Usage Log"
        verbose_name_plural = "API Usage Logs"
        indexes = [  # Your existing indexes are good
            models.Index(fields=['user', 'api_name', 'timestamp']),
            models.Index(fields=['api_name', 'operation']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['request_id']),  # Added index for request_id
        ]

    def __str__(self):
        user_str = self.user.username if self.user else "System"
        operation_str = self.get_operation_display() if self.operation else self.operation
        status_str = self.get_status_display() if self.status else self.status
        return f"{self.get_api_name_display()} - {operation_str} ({status_str}) by {user_str} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def _calculate_cost_value(self):
        """Internal helper to calculate cost without saving."""
        # These should ideally come from settings or a more dynamic configuration model/service
        COST_PER_TOKEN_MAP = {
            'chatgpt': {
                'input': 0.0000005,  # Example: $0.50 / 1M tokens for GPT-3.5 Turbo input
                'output': 0.0000015,  # Example: $1.50 / 1M tokens for GPT-3.5 Turbo output
            },
            'gemini': {  # Example for Gemini 1.0 Pro
                'input': 0.000000125,
                'output': 0.000000375,
            }
            # Add other models/APIs as needed
        }

        calculated_cost = 0.0
        api_key_to_check = None

        if self.api_name:  # Check if api_name is set
            if 'chatgpt' in self.api_name.lower():
                api_key_to_check = 'chatgpt'
            elif 'gemini' in self.api_name.lower():
                api_key_to_check = 'gemini'
            # Add more specific checks if needed, e.g., self.api_name == 'chatgpt-4'

        if api_key_to_check:
            rates = COST_PER_TOKEN_MAP.get(api_key_to_check, {})
            input_cost = (self.input_tokens or 0) * rates.get('input', 0)
            output_cost = (self.output_tokens or 0) * rates.get('output', 0)
            calculated_cost = float(input_cost) + float(output_cost)

        return calculated_cost

    def save(self, *args, **kwargs):
        self.total_tokens = (self.input_tokens or 0) + (self.output_tokens or 0)
        self.cost = self._calculate_cost_value()  # Call helper to get cost
        super().save(*args, **kwargs)



# def resume_upload_path(instance, filename):
#     """Generate a unique path for uploaded resume files."""
#     # Generate a unique filename with original extension
#     ext = filename.split('.')[-1]
#     filename = f"{uuid.uuid4()}.{ext}"
#     # Return path like 'resumes/user_1/2023/03/filename.pdf'
#     return os.path.join(
#         'resumes',
#         f"user_{instance.user.id}",
#         str(timezone.now().year),
#         str(timezone.now().month),
#         filename
#     )
# class Resume(models.Model):
#     STATUS_CHOICES = [
#         ('created', 'Created'),
#         ('uploaded', 'Uploaded'),
#         ('generated', 'Generated'),
#         ('failed', 'Failed')
#     ]
#
#
#     first_name = models.CharField(max_length=100)
#     mid_name = models.CharField(max_length=100, blank=True)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(unique=False)
#     phone = models.CharField(max_length=15)
#     address = models.TextField(blank=True, null=True)
#     linkedin = models.URLField(blank=True, null=True)
#     github = models.URLField(blank=True, null=True)
#     portfolio = models.URLField(blank=True, null=True)
#     summary = models.TextField(blank=True, null=True, validators=[MinLengthValidator(100)])
#
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='resumes')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='uploaded')
#
#     class Meta:
#         ordering = ['-created_at']
#
#     def __str__(self):
#         return f"{self.first_name} {self.last_name}"
#
#     @property
#     def full_name(self):
#         return f"{self.first_name} {self.mid_name} {self.last_name}".strip()


# class Skill(models.Model):
#     SKILL_TYPES = [
#         ('technical', 'Technical'),
#         ('soft', 'Soft'),
#         ('language', 'Language'),
#         ('tool', 'Tool')
#     ]
#
#     resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='skills')
#     skill_name = models.CharField(max_length=50)
#     skill_type = models.CharField(max_length=20, choices=SKILL_TYPES, default='technical')
#     proficiency_level = models.IntegerField(default=0)
#
#     class Meta:
#         ordering = ['skill_type', '-proficiency_level']
#
#     def __str__(self):
#         return self.skill_name






# class Experience(models.Model):
#     resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='experiences')
#     job_title = models.CharField(max_length=100)
#     employer = models.CharField(max_length=100)
#     location = models.CharField(max_length=100)
#     start_date = models.DateField()
#     end_date = models.DateField(blank=True, null=True)
#     is_current = models.BooleanField(default=False)
#
#     class Meta:
#         ordering = ['-start_date']
#
#     def __str__(self):
#         return f"{self.job_title} at {self.employer}"


# class ExperienceBulletPoint(models.Model):
#     experience = models.ForeignKey(Experience, on_delete=models.CASCADE, related_name='bullet_points')
#     description = models.TextField()
#     keywords = models.ManyToManyField('Keyword', blank=True)
#
#     def __str__(self):
#         return f"Bullet Point for {self.experience.job_title}"


# class Education(models.Model):
#     DEGREE_TYPES = [
#         ('high_school', 'High School'),
#         ('associate', 'Associate Degree'),
#         ('bachelor', "Bachelor's Degree"),
#         ('master', "Master's Degree"),
#         ('doctorate', 'Doctorate'),
#         ('other', 'Other')
#     ]
#
#     resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='educations')
#     school_name = models.CharField(max_length=100)
#     location = models.CharField(max_length=100)
#     degree = models.CharField(max_length=100)
#     degree_type = models.CharField(max_length=20, choices=DEGREE_TYPES, default='bachelor')
#     field_of_study = models.CharField(max_length=100)
#     graduation_date = models.DateField(blank=True, null=True)
#     gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
#
#     class Meta:
#         ordering = ['-graduation_date']
#
#     def __str__(self):
#         return f"{self.degree} at {self.school_name}"


# class Certification(models.Model):
#     resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='certifications')
#     name = models.CharField(max_length=100)
#     institute = models.CharField(max_length=100, blank=True, null=True)
#     completion_date = models.DateField(blank=True, null=True)
#     expiration_date = models.DateField(blank=True, null=True)
#     score = models.CharField(max_length=50, blank=True, null=True)
#     link = models.URLField(blank=True, null=True)
#     description = models.TextField(blank=True, null=True)
#
#     class Meta:
#         ordering = ['-completion_date']
#
#     def __str__(self):
#         return self.name


# class Project(models.Model):
#     resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='projects')
#     project_name = models.CharField(max_length=100)
#     summary = models.TextField(blank=True, null=True)
#     technologies = models.ManyToManyField(Skill, blank=True)
#     start_date = models.DateField(blank=True, null=True)
#     completion_date = models.DateField(blank=True, null=True)
#     project_link = models.URLField(blank=True, null=True)
#     github_link = models.URLField(blank=True, null=True)
#
#     class Meta:
#         ordering = ['-completion_date']
#
#     def __str__(self):
#         return self.project_name


# class ProjectBulletPoint(models.Model):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bullet_points')
#     description = models.TextField()
#     keywords = models.ManyToManyField('Keyword', blank=True)
#
#     def __str__(self):
#         return f"Bullet Point for {self.project.project_name}"


# class Language(models.Model):
#     PROFICIENCY_LEVELS = [
#         ('basic', 'Basic'),
#         ('intermediate', 'Intermediate'),
#         ('advanced', 'Advanced'),
#         ('native', 'Native')
#     ]
#
#     resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='languages')
#     language_name = models.CharField(max_length=100)
#     proficiency = models.CharField(max_length=20, choices=PROFICIENCY_LEVELS, default='basic')
#
#     def __str__(self):
#         return f"{self.language_name} ({self.proficiency})"


# class CustomData(models.Model):
#     resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='custom_data')
#     name = models.CharField(max_length=100, help_text="Type of data (e.g., Achievements, Awards, Hobbies)")
#     completion_date = models.DateField(blank=True, null=True)
#     bullet_points = models.TextField(help_text="Add bullet points, one per line", blank=True, null=True)
#     description = models.TextField(blank=True, null=True)
#     link = models.URLField(blank=True, null=True)
#     institution_name = models.CharField(max_length=100, blank=True, null=True)
#
#     class Meta:
#         ordering = ['-completion_date']
#
#     def __str__(self):
#         return self.name


# class JobInput(models.Model):
#     STATUS_CHOICES = [
#
#         ('completed', 'Completed'),
#         ('resume_created', 'Resume_Created'),
#         ('resume_keyword_created', 'Resume_Keyword_Created'),
#         ('failed', 'Failed'),
#     ]
#
#     AI_CHOICES = [
#         ('chatgpt', 'ChatGPT'),
#         ('gemini', 'Gemini'),
#     ]
#
#     company_name = models.CharField(max_length=100)
#     job_post = models.CharField(max_length=100)
#     job_description = models.TextField()
#     job_post_url = models.URLField(blank=True, null=True)
#     ai_choice = models.CharField(max_length=20, choices=AI_CHOICES, default='chatgpt')
#
#     recruiter_name = models.CharField(max_length=100, blank=True, null=True)
#     recruiter_email = models.EmailField(blank=True, null=True)
#     recruiter_linkedin = models.URLField(blank=True, null=True)
#
#     reference_name = models.CharField(max_length=100, blank=True, null=True)
#     reference_email = models.EmailField(blank=True, null=True)
#     reference_linkedin = models.URLField(blank=True, null=True)
#
#     resume_file = models.FileField(
#         upload_to=resume_upload_path,
#         validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
#         blank=True,
#         null=True
#     )
#
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = "Job Input"
#         verbose_name_plural = "Job Inputs"
#
#     def __str__(self):
#         return f"{self.company_name} - {self.job_post}"


# class Keyword(models.Model):
#     KEYWORD_TYPES = [
#         ('technical', 'Technical Skill'),
#         ('soft', 'Soft Skill'),
#         ('qualification', 'Qualification'),
#         ('requirement', 'Requirement')
#     ]
#
#     job_input = models.ForeignKey(JobInput, on_delete=models.CASCADE, related_name='keywords')
#     keyword = models.CharField(max_length=100)
#     category = models.CharField(max_length=20, choices=KEYWORD_TYPES, default='technical')
#     relevance_score = models.FloatField(default=1.0)
#     is_matched = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         ordering = ['-relevance_score']
#
#     def __str__(self):
#         return f"{self.keyword} ({self.category})"


# class AIProcessingLog(models.Model):
#     job_input = models.ForeignKey(JobInput, on_delete=models.CASCADE, related_name='processing_logs')
#     process_type = models.CharField(max_length=50)
#     status = models.CharField(max_length=20)
#     error_message = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     completed_at = models.DateTimeField(blank=True, null=True)
#
#     class Meta:
#         ordering = ['-created_at']
#
#     def __str__(self):
#         return f"{self.process_type} - {self.status}"


# class APIUsage(models.Model):
#     """
#     Tracks API usage and costs for different AI services
#     """
#     API_CHOICES = [
#         ('chatgpt', 'ChatGPT'),
#         ('gemini', 'Gemini')
#     ]
#
#     OPERATION_TYPES = [
#         ('keyword_extraction', 'Keyword Extraction'),
#         ('resume_parsing', 'Resume Parsing'),
#         ('content_generation', 'Content Generation'),
#         ('analysis', 'Analysis')
#     ]
#
#     STATUS_CHOICES = [
#         ('success', 'Success'),
#         ('failed', 'Failed'),
#         ('error', 'Error')
#     ]
#
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='api_usage')
#     job_input = models.ForeignKey('JobInput', on_delete=models.CASCADE, related_name='api_usage', null=True)
#
#     # API Details
#     api_name = models.CharField(max_length=20, choices=API_CHOICES)
#     operation = models.CharField(max_length=50, choices=OPERATION_TYPES)
#
#     # Usage Metrics
#     input_tokens = models.IntegerField(default=0)
#     output_tokens = models.IntegerField(default=0)
#     total_tokens = models.IntegerField(default=0)
#     cost = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
#
#     # Performance Metrics
#     response_time = models.FloatField(help_text="API response time in seconds", default=0.0)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
#     error_message = models.TextField(blank=True, null=True)
#
#     # Metadata
#     timestamp = models.DateTimeField(auto_now_add=True)
#     request_id = models.CharField(max_length=100, blank=True, null=True)
#
#     class Meta:
#         ordering = ['-timestamp']
#         indexes = [
#             models.Index(fields=['user', 'api_name', 'timestamp']),
#             models.Index(fields=['api_name', 'operation']),
#             models.Index(fields=['timestamp'])
#         ]
#
#     def __str__(self):
#         return f"{self.api_name} - {self.operation} ({self.timestamp})"
#
#     def calculate_cost(self):
#         """Calculate cost based on tokens used"""
#         COST_PER_TOKEN = {
#             'chatgpt': {
#                 'input': 0.0000015,  # \$0.0015 per 1K tokens
#                 'output': 0.000002  # \$0.002 per 1K tokens
#             },
#             'gemini': {
#                 'input': 0.0000005,  # \$0.0005 per 1K tokens
#                 'output': 0.0000005  # $0.0005 per 1K tokens
#             }
#         }
#
#         if self.api_name in COST_PER_TOKEN:
#             costs = COST_PER_TOKEN[self.api_name]
#             self.cost = (
#                     (self.input_tokens * costs['input']) +
#                     (self.output_tokens * costs['output'])
#             )
#             self.total_tokens = self.input_tokens + self.output_tokens
#             self.save()
#
#         return self.cost


