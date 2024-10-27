from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Post(models.Model):
    title = models.CharField(max_length=200)  # Title
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User
    user_image = models.ImageField(upload_to='user_images/', blank=True, null=True)  # User Avatar Image
    object_image = models.ImageField(upload_to='object_images/', blank=True, null=True)  # Object Image
    description = models.TextField()  # Description
    created_at = models.DateTimeField(auto_now_add=True)  # Created Date

    def __str__(self):
        return self.title
    