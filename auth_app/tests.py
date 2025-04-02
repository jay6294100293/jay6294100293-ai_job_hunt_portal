# auth_app/tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()  # Get the custom user model

class UserRegistrationTest(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.email = 'testuser@example.com'
        self.password = 'password123'

    def test_user_can_signup(self):
        response = self.client.post(reverse('signup'), {
            'username': self.username,
            'email': self.email,
            'password1': self.password,
            'password2': self.password,
        })
        self.assertEqual(response.status_code, 302)  # Check for redirection
        self.assertTrue(User.objects.filter(username=self.username).exists())

    def test_signup_creates_user(self):
        self.client.post(reverse('signup'), {
            'username': self.username,
            'email': self.email,
            'password1': self.password,
            'password2': self.password,
        })
        user = User.objects.get(username=self.username)
        self.assertEqual(user.email, self.email)

class UserLoginTest(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.email = 'testuser@example.com'
        self.password = 'password123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)

    def test_user_can_login(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, 302)  # Check for successful login and redirection
        self.assertContains(response, f"Welcome, {self.username}")  # Check dashboard content

    def test_login_with_incorrect_password(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'wrongpassword123',
        })
        self.assertEqual(response.status_code, 200)  # Should stay on the login page
        self.assertFormError(response, 'form', None, 'Please enter a correct username and password.')  # Adjust as needed

class PasswordResetTest(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.email = 'testuser@example.com'
        self.password = 'password123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)

    def test_password_reset_request_sends_email(self):
        response = self.client.post(reverse('password_reset'), {'email': self.email})

        self.assertEqual(response.status_code, 302)  # Check redirection after successful request
        self.assertEqual(len(mail.outbox), 1)  # One email should be sent
        self.assertEqual(mail.outbox[0].subject, 'Password Reset Requested')  # Check email subject
        self.assertIn("To reset your password", mail.outbox[0].body)  # Check body content

    def test_password_reset_confirm(self):
        response = self.client.post(reverse('password_reset'), {'email': self.email})
        token = mail.outbox[0].body.split('token=')[1].strip()  # Extract token from email body
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        new_password = 'newpassword123'
        response = self.client.post(reverse('password_reset_confirm', kwargs={
            'uidb64': uid,
            'token': token,
        }), {
            'new_password1': new_password,
            'new_password2': new_password,
        })

        self.assertEqual(response.status_code, 302)  # Check for successful password reset
        self.assertTrue(User.objects.get(username=self.username).check_password(new_password))  # Validate new password

    def test_password_reset_invalid_token(self):
        response = self.client.post(reverse('password_reset_confirm', kwargs={
            'uidb64': urlsafe_base64_encode(force_bytes(self.user.pk)),
            'token': 'invalid_token',
        }), {
            'new_password1': 'newpassword123',
            'new_password2': 'newpassword123',
        })

        self.assertEqual(response.status_code, 200)  # Should stay on the reset page

class DashboardTest(TestCase):
    def setUp(self):
        self.username = 'testuser_dashboard'
        self.email = 'testuser_dashboard@example.com'
        self.password = 'password123'
        self.user = User.objects.create_user(username=self.username, email=self.email, password=self.password)

    def test_dashboard_access(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)  # Access should be allowed
        self.assertContains(response, f"Welcome, {self.username}")

    def test_dashboard_access_without_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}", status_code=302)  # Redirect to login
