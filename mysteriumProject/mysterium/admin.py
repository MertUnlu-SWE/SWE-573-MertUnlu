from django.contrib import admin
from .models import Post, Comment, Bookmark

# Register your models here.
admin.site.register(Post)

# Register Comment model
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'text', 'created_at')  # Fields visible in the list
    search_fields = ('text', 'user__username', 'post__title')  # Add search functionality
    list_filter = ('created_at', 'user')  # Add filters for easy navigation
    ordering = ('-created_at',)  # Default ordering by creation date

    def bookmark_count(self, obj):
        return obj.bookmarked_by.count()  # Display the number of bookmarks for each comment
    bookmark_count.short_description = 'Bookmark Count'
    
    # Optional: Add inline editing for post comments
    class Media:
        css = {
            'all': ('custom_admin.css',)  # Optional custom styling
        }

# Register Bookmark model
@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'created_at')  # Display these fields in the admin panel
    search_fields = ('user__username', 'comment__text')  # Add search functionality
    list_filter = ('created_at', 'user')  # Add filters for easy navigation
    ordering = ('-created_at',)  # Default ordering by creation date