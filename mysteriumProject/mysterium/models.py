from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=200)  # Title
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User
    user_image = models.ImageField(
        upload_to='user_images/', blank=True, null=True)  # User Avatar Image
    object_image = models.ImageField(
        upload_to='object_images/', blank=True, null=True)  # Object Image
    description = models.TextField()  # Description
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    voted_users = models.ManyToManyField(User, related_name="voted_posts", blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags.")
    created_at = models.DateTimeField(auto_now_add=True)  # Created Date

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    voted_users = models.ManyToManyField(User, related_name="voted_comments", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
