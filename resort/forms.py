import unicodedata

from django import forms
from django.core.exceptions import ValidationError

from .models import ContactRequest


class ContactRequestForm(forms.ModelForm):
    message = forms.CharField(
        min_length=10,
        max_length=5000,
        error_messages={
            'min_length': 'Please add a little more detail (at least 10 characters).',
        },
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Your message...',
            'aria-describedby': 'message-feedback message-server-errors',
        }),
    )

    class Meta:
        model = ContactRequest
        fields = ('fullname', 'email', 'phone', 'message')
        widgets = {
            'fullname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name',
                'aria-describedby': 'fullname-feedback fullname-server-errors',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com',
                'aria-describedby': 'email-feedback email-server-errors',
            }),
            'phone': forms.TelInput(attrs={
                'class': 'form-control',
                'placeholder': '+355 6X XXX XXX',
                'aria-describedby': 'phone-feedback phone-server-errors',
            }),
        }

    def clean_fullname(self):
        fullname = self.cleaned_data['fullname']
        allowed_punctuation = {" ", "-", "'", "’", "."}
        if len(fullname) < 2:
            raise ValidationError(
                'Enter at least 2 characters for your name.',
                code='min_length',
            )
        if not any(character.isalpha() for character in fullname) or any(
            not (
                character.isalpha()
                or unicodedata.category(character).startswith('M')
                or character in allowed_punctuation
            )
            for character in fullname
        ):
            raise ValidationError(
                'Use letters only; spaces, hyphens, apostrophes and periods are allowed.',
                code='invalid_name',
            )
        return fullname
