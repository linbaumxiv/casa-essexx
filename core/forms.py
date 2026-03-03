from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Review

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'is_vendor', 'is_buyer')

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }