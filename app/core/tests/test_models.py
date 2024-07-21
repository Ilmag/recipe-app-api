"""
Tests for models
"""
from django.test import TestCase # noqa
from django.contrib.auth import get_user_model # noqa

class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_successful(self):
        """Test creating user with email is successful"""
        email = 'test@example.com'
        password = 'samplepass1234'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.password, password)
