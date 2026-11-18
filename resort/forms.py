import re
import unicodedata

from django import forms
from django.core.exceptions import ValidationError

from .models import ContactRequest, Villa

PHONE_PATTERN = re.compile(r'\+?[0-9\s().-]+')


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

    # Vila që e intereson klientin. Vlera është slug-u, që faqja e vilës ta zgjedhë vetë
    # përmes /contact/?villa=<slug>. Lejohen vetëm vilat e publikuara.
    villa = forms.ModelChoiceField(
        queryset=Villa.objects.none(),
        required=False,
        to_field_name='slug',
        empty_label='Not sure yet / any villa',
        label='Villa of interest',
        error_messages={'invalid_choice': 'Please choose one of the listed villas.'},
        widget=forms.Select(attrs={
            'class': 'form-select',
            'aria-describedby': 'villa-server-errors',
        }),
    )

    # Honeypot: fushë e fshehur për njerëzit; bot-et e mbushin dhe kërkesa hidhet poshtë.
    website = forms.CharField(
        required=False,
        label='Leave this field empty',
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'tabindex': '-1'}),
    )

    class Meta:
        model = ContactRequest
        fields = ('fullname', 'email', 'phone', 'villa', 'message')
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['villa'].queryset = Villa.objects.filter(
            is_published=True,
            villa_type__is_active=True,
        )

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

    def clean_phone(self):
        # Same rule as form-validation.js: digits with optional +, spaces, (), . and -.
        phone = self.cleaned_data['phone'].strip()
        digits = sum(character.isdigit() for character in phone)
        if not PHONE_PATTERN.fullmatch(phone) or not 7 <= digits <= 15:
            raise ValidationError(
                'Enter a valid phone number (7-15 digits).',
                code='invalid_phone',
            )
        return phone

    def is_spam(self):
        return bool(self.cleaned_data.get('website'))
