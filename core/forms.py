from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User, Review


class CustomUserCreationForm(UserCreationForm):
    """
    Form for registering a new user with choice of role (Vendor or Buyer).
    """
    
    class Meta(UserCreationForm.Meta):
        model = User
        # Adding email and role flags to the default UserCreationForm
        fields = UserCreationForm.Meta.fields + ('email', 'is_vendor', 'is_buyer')


class ReviewForm(forms.ModelForm):
    """
    Form for customers to leave feedback on products.
    """
    
    # Defining specific choices for the rating to ensure data integrity (1-5)
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