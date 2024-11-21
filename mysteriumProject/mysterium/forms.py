from django import forms
from .models import Comment, Post
from .wikidata_utils import fetch_wikidata_info


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
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter tags separated by commas'}),
        required=False,
        help_text="Add tags separated by commas (e.g., 'metal, red, 10cm')."
    )

    class Meta:
        model = Post
        fields = ['title', 'description', 'object_image', 'tags']

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

        tags_with_wikidata = []
        for tag in tag_list:
            try:
                wikidata_id, _ = fetch_wikidata_info(tag)
                if wikidata_id:
                    tags_with_wikidata.append(f"{tag} (Q{wikidata_id})")
                else:
                    tags_with_wikidata.append(tag)
            except Exception as e:
                raise forms.ValidationError(
                    f"Error processing tag '{tag}': {
                        e}. Please try again or contact support."
                )

        return ','.join(tags_with_wikidata)
