from django import forms

from .models import ContactMessage


class ContactMessageForm(forms.ModelForm):
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
        model = ContactMessage
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
