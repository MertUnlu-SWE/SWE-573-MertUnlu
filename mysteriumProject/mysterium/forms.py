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


class AdvancedSearchForm(forms.Form):
    title = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Search by title...', 'class': 'form-control'})
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('none', 'None'),
            ('date', 'Date'),
            ('title', 'Title'),
            ('solved', 'Solved'),
            ('upvotes', 'Upvotes'),
            ('comments', 'Comments')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Min Price', 'class': 'form-control'})
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Max Price', 'class': 'form-control'})
    )
    color = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Color', 'class': 'form-control'})
    )
    material = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Material', 'class': 'form-control'})
    )
    volume = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Volume (e.g., 500ml)', 'class': 'form-control'})
    )
    width = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Width (e.g., 10cm)', 'class': 'form-control'})
    )
    height = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Height (e.g., 15cm)', 'class': 'form-control'})
    )
    length = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Length (e.g., 20cm)', 'class': 'form-control'})
    )
    weight = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Weight (e.g., 500g)', 'class': 'form-control'})
    )
    condition = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Condition (e.g., New, Worn)', 'class': 'form-control'})
    )
    shape = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Shape (e.g., Cylindrical)', 'class': 'form-control'})
    )
    physical_state = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Physical State (e.g., Solid, Liquid)', 'class': 'form-control'})
    )
    sound = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Sound (e.g., Silent, Loud)', 'class': 'form-control'})
    )
    taste = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Taste (e.g., Bitter)', 'class': 'form-control'})
    )
    smell = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Smell (e.g., Floral)', 'class': 'form-control'})
    )
    functionality = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Functionality (e.g., Cutting wood)', 'class': 'form-control'})
    )
    location = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.Textarea(attrs={'placeholder': 'Location (e.g., Found in Norway)', 'class': 'form-control', 'rows': 2})
    )
    markings = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.Textarea(attrs={'placeholder': 'Markings (e.g., Symbols, Numbers)', 'class': 'form-control', 'rows': 2})
    )
    historical_context = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.Textarea(attrs={'placeholder': 'Historical Context (e.g., 18th century)', 'class': 'form-control', 'rows': 2})
    )
    distinctive_features = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.Textarea(attrs={'placeholder': 'Distinctive Features (e.g., Unique patterns)', 'class': 'form-control', 'rows': 2})
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter tags separated by commas...', 'class': 'form-control'})
    )




class PostForm(forms.ModelForm):
    volume = forms.CharField(
    required=False, 
    widget=forms.TextInput(attrs={'id': 'volume', 'placeholder': 'e.g., 500ml'})
    )

    width = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'id': 'width', 'placeholder': 'e.g., 10cm'})
    )

    height = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'id': 'height', 'placeholder': 'e.g., 15cm'})
    )

    length = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'id': 'length', 'placeholder': 'e.g., 20cm'})
    )

    price = forms.DecimalField(
        required=False, 
        max_digits=10, 
        decimal_places=2, 
        widget=forms.TextInput(attrs={'id': 'price', 'placeholder': 'e.g., 150.00'}),
        error_messages={
            'invalid': "Please enter a valid price in the format '123.45'."
        }
    )

    shape = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'id': 'shape', 'placeholder': 'e.g., Cylindrical'})
    )

    physical_state = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'id': 'physical_state', 'placeholder': 'e.g., Solid'})
    )

    color = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'id': 'color', 'placeholder': 'e.g., Red'})
    )

    sound = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'id': 'sound', 'placeholder': 'e.g., Silent'})
    )

    can_be_disassembled = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={'id': 'can_be_disassembled'})
    )

    taste = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'id': 'taste', 'placeholder': 'e.g., Bitter'})
    )

    smell = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'id': 'smell', 'placeholder': 'e.g., Floral'})
    )

    functionality = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'id': 'functionality', 'placeholder': 'e.g., Used for cutting wood'})
    )

    location = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'id': 'location', 'placeholder': 'e.g., Found in a forest in Norway'})
    )

    distinctive_features = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'id': 'distinctive_features', 'placeholder': 'e.g., Unique patterns, unusual texture'})
    )

    historical_context = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={'id': 'historical_context', 'placeholder': 'e.g., Timezone, 1500 BC'})
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
            'title', 'description', 'object_image', 'material',
            'weight', 'condition', 'markings', 'historical_context',
            'distinctive_features', 'volume', 'width', 'height', 'length',
            'price', 'shape', 'physical_state', 'color', 'sound',
            'can_be_disassembled', 'taste', 'smell', 'functionality',
            'location', 'tags'
        ]

    def clean_object_image(self):
        object_image = self.cleaned_data.get('object_image')
        if not object_image:
            raise forms.ValidationError("An image is required for the post.")
        return object_image

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

