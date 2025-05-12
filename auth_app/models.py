from django.db import models

# Create your models here.
# auth_app/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

# class CustomUser(AbstractUser):
#     email = models.EmailField(unique=True)
#     profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
#     phone_number = models.CharField(max_length=15, blank=True)
#     is_verified = models.BooleanField(default=False)
#     api_key_limit = models.IntegerField(default=100)
#     subscription_type = models.CharField(max_length=20, default='free')
#     chatgpt_api_key = models.CharField(max_length=255, blank=True, null=True)
#     gemini_api_key = models.CharField(max_length=255, blank=True, null=True)
#
#     def __str__(self):
#         return self.email


# auth_app/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _  # For help_text best practice


# Helper function for profile picture upload path (if you don't have one already)
def profile_pics_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"  # Requires import uuid
    return os.path.join('profile_pics', f'user_{instance.id}', filename)  # Requires import os


import os  # Add this if not present
import uuid  # Add this if not present


class CustomUser(AbstractUser):
    # Existing fields from AbstractUser: username, first_name, last_name, is_staff, is_active, date_joined
    # Your existing custom fields:
    email = models.EmailField(_('email address'), unique=True)  # Explicitly set verbose_name, unique=True is good.

    profile_picture = models.ImageField(
        upload_to='profile_pics/',  # Consider using the helper function: profile_pics_upload_path
        null=True,
        blank=True,
        help_text=_("User's profile picture.")
    )
    # 'phone_number' you already have, perfect for matching Resume.phone
    phone_number = models.CharField(
        _("phone number"),
        max_length=20,  # Increased to 20 for international consistency
        blank=True,
        help_text=_("User's primary phone number (e.g., for profile).")
    )
    is_verified = models.BooleanField(default=False)
    api_key_limit = models.IntegerField(default=100)
    subscription_type = models.CharField(max_length=20, default='free')  # Consider choices here if you have fixed types

    # API keys can remain here or on the APIKey model. Your APIKey model is fine.
    # Storing them directly here might be okay if they are few and central to the user.
    # If you keep the APIKey model, these two might be redundant here unless for a different purpose.
    # For now, I'll assume they are as you intend.
    chatgpt_api_key = models.CharField(max_length=255, blank=True, null=True)
    gemini_api_key = models.CharField(max_length=255, blank=True, null=True)

    # --- NEW FIELDS FOR "CORE PROFILE DETAILS" to be imported into Resume ---
    default_address = models.TextField(
        _("default address"),
        blank=True,
        null=True,
        help_text=_("User's primary address (e.g., for profile).")
    )
    default_linkedin_url = models.URLField(
        _("default LinkedIn URL"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Link to user's LinkedIn profile.")
    )
    default_github_url = models.URLField(
        _("default GitHub URL"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Link to user's GitHub profile.")
    )
    default_portfolio_url = models.URLField(
        _("default portfolio URL"),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Link to user's personal portfolio or website.")
    )
    default_summary = models.TextField(
        _("default professional summary"),
        blank=True,
        null=True,
        help_text=_("User's default professional summary for their profile.")
    )

    # If you want to use email as the primary identifier for login:
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username'] # Or [] if username is not required anymore

    def __str__(self):
        return self.username  # Changed back to username as it's more common for AbstractUser's __str__
        # Your choice of self.email is also fine if you prefer.


# Your APIKey model (remains unchanged, assuming it's still needed separately)
class APIKey(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='api_key_custom')  # Changed related_name to avoid clash if you had one before
    openai_api_key = models.CharField(max_length=255, blank=True, null=True)
    gemini_api_key = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"API Keys for {self.user.username}"