from django import forms
from .models import Comment, Post

class CommentForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter your comment...',
            'rows': 4,
            'cols': 40
        }),
        label='',
        required=True)
    class Meta:
        model = Comment
        fields = ['text']

class PostForm(forms.ModelForm):
    tags = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter tags separated by commas'}),
        required=False,
        help_text="Add tags separated by commas (e.g., 'metal, 10cm, red')."
    )

    class Meta:
        model = Post
        fields = ['title', 'description', 'object_image', 'tags']

