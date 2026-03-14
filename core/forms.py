from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Review

class CustomUserCreationForm(UserCreationForm):
    """
    Form for registering a new user with a mandatory choice of role.
    Replaces checkboxes with a dropdown to prevent dual-role profiles.
    """
    
    # Defining the dropdown options
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('vendor', 'Vendor'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label="I want to register as a:"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Removed the individual boolean flags from 'fields'
        fields = UserCreationForm.Meta.fields + ('email', 'role')

    def save(self, commit=True):
        """
        Custom save logic to translate the dropdown selection into
        the model's boolean flags.
        """
        user = super().save(commit=False)
        role_choice = self.cleaned_data.get('role')

        if role_choice == 'vendor':
            user.is_vendor = True
            user.is_buyer = False
        else:
            user.is_vendor = False
            user.is_buyer = True

        if commit:
            user.save()
        return user


class ReviewForm(forms.ModelForm):
    """
    Form for customers to leave feedback on products.
    """
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(
                attrs={
                    'rows': 3, 
                    'class': 'form-control', 
                    'placeholder': 'Share your thoughts on this product...'
                }
            ),
        }