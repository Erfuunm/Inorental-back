from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # userId is inherited from AbstractUser as id
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)
    profile_picture_url = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # username is required by AbstractUser, but we use email for login

    def __str__(self):
        return self.email
