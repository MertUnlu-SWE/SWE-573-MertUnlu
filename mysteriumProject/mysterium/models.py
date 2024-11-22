from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=200)  # Title
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User
    user_image = models.ImageField(upload_to='user_images/', blank=True, null=True)  # User Avatar Image
    object_image = models.ImageField(upload_to='object_images/', blank=True, null=True)  # Object Image
    description = models.TextField()  # Description
    material = models.CharField(max_length=100, blank=True, null=True)  # Material
    dimensions = models.CharField(max_length=100, blank=True, null=True)  # Dimensions
    weight = models.CharField(max_length=50, blank=True, null=True)  # Weight
    condition = models.CharField(max_length=100, blank=True, null=True)  # Condition
    markings = models.TextField(blank=True, null=True)  # Markings or Text
    historical_context = models.TextField(blank=True, null=True)  # Historical Context
    distinctive_features = models.TextField(blank=True, null=True)  # Distinctive Features
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags.")
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    voted_users = models.ManyToManyField(User, related_name="voted_posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Created Date
    is_solved = models.BooleanField(default=False)  # Post Solved
    solved_comment = models.ForeignKey(
        'Comment',  # Comment section reference
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solved_posts',
        help_text="The comment that solves this post."
    )

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
