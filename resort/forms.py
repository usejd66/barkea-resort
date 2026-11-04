from django import forms

from .models import ContactMessage


class ContactMessageForm(forms.ModelForm):
    message = forms.CharField(
        max_length=5000,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Your message...',
        }),
    )

    class Meta:
        model = ContactMessage
        fields = ('fullname', 'email', 'phone', 'message')
        widgets = {
            'fullname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'phone': forms.TelInput(attrs={'class': 'form-control', 'placeholder': '+355 6X XXX XXX'}),
        }
