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
    material = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Metal, Plastic'})
    )
    dimensions = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 10cm x 5cm x 2cm'})
    )
    weight = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 500g'})
    )
    condition = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., New, Worn, Damaged'})
    )
    markings = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'e.g., Symbols, Numbers, Inscriptions'
        })
    )
    historical_context = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'e.g., Likely from the 18th century'
        })
    )
    distinctive_features = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'e.g., Unique patterns, unusual texture'
        })
    )

    tags = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter tags separated by commas'}),
        required=False,
        help_text="Add tags separated by commas (e.g., 'metal, red, 10cm')."
    )

    class Meta:
        model = Post
        fields = [
            'title', 'description', 'object_image', 'material', 'dimensions',
            'weight', 'condition', 'markings', 'historical_context', 'distinctive_features', 'tags'
        ]

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
                    f"Error processing tag '{tag}': {e}. Please try again or contact support."
                )

        return ','.join(tags_with_wikidata)

