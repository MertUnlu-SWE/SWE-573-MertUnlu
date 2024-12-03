from django.contrib import admin
from .models import Post, Comment

# Register your models here.
admin.site.register(Post)

# Register Comment model
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'text', 'created_at')  # Fields visible in the list
    search_fields = ('text', 'user__username', 'post__title')  # Add search functionality
    list_filter = ('created_at', 'user')  # Add filters for easy navigation
    ordering = ('-created_at',)  # Default ordering by creation date

    # Optional: Add inline editing for post comments
    class Media:
        css = {
            'all': ('custom_admin.css',)  # Optional custom styling
        }