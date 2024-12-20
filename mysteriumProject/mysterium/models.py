from django.db import models
from django.conf import settings
import boto3
from django.contrib.auth.models import User

UNIT_CHOICES = [
    ('cm', 'Centimeter'),
    ('m', 'Meter'),
    ('g', 'Gram'),
    ('kg', 'Kilogram'),
    ('USD', 'USD'),
    ('EUR', 'Euro'),
    ('TRY', 'TRY'),
]

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)  # Title
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User
    user_image = models.ImageField(upload_to='user_images/', blank=True, null=True)  # User Avatar Image
    object_image = models.ImageField(upload_to='object_images/', blank=True, null=True)  # Object Image
    description = models.TextField()  # Description
    material = models.CharField(max_length=100, blank=True, null=True)
    weight = models.CharField(max_length=50, blank=True, null=True)
    condition = models.CharField(max_length=100, blank=True, null=True)
    markings = models.TextField(blank=True, null=True)
    historical_context = models.TextField(blank=True, null=True)
    distinctive_features = models.TextField(blank=True, null=True)
    volume = models.CharField(max_length=50, blank=True, null=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    width_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='cm')
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    height_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='cm')
    length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    length_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='cm')
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    weight_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='g')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='USD')
    shape = models.CharField(max_length=100, blank=True, null=True)
    physical_state = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    sound = models.CharField(max_length=100, blank=True, null=True)
    can_be_disassembled = models.BooleanField(default=False)
    taste = models.CharField(max_length=100, blank=True, null=True)
    smell = models.CharField(max_length=100, blank=True, null=True)
    functionality = models.TextField(blank=True, null=True)
    location = models.TextField(blank=True, null=True)
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

    def delete(self, *args, **kwargs):
        if self.object_image:
            try:
                s3 = boto3.client('s3')
                bucket_name = settings.AWS_STORAGE_BUCKET_NAME
                s3.delete_object(Bucket=bucket_name, Key=self.object_image.name)
            except Exception as e:
                print(f"Error deleting {self.object_image.name}: {e}")
        super().delete(*args, **kwargs)

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


class Vote(models.Model):
    VOTE_TYPES = [('upvote', 'Upvote'), ('downvote', 'Downvote')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=10, choices=VOTE_TYPES)

    class Meta:
        unique_together = ('user', 'post')  # Ensure a user can vote only once per post


class CommentVote(models.Model):
    VOTE_TYPES = [('upvote', 'Upvote'), ('downvote', 'Downvote')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_votes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=10, choices=VOTE_TYPES)

    class Meta:
        unique_together = ('user', 'comment')  # Ensure a user can vote only once per comment


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarked_comments')
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')
