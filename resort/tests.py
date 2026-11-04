from django.core import mail
from django.test import TestCase, override_settings

from .models import ContactMessage


class PublicPagesTests(TestCase):
    def test_public_pages_render(self):
        for url in ('/', '/about/', '/villas/', '/gallery/', '/location/', '/contact/'):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_unknown_villa_returns_404(self):
        response = self.client.get('/villas/999/')
        self.assertEqual(response.status_code, 404)


class ContactMessageTests(TestCase):
    def test_valid_contact_submission_is_saved(self):
        response = self.client.post('/contact/', {
            'fullname': 'Test Visitor',
            'email': 'visitor@example.com',
            'phone': '+355 69 123 4567',
            'message': 'I would like to schedule a visit.',
        })

        self.assertRedirects(response, '/contact/')
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(ContactMessage.objects.get().email, 'visitor@example.com')

    def test_invalid_contact_submission_is_not_saved(self):
        response = self.client.post('/contact/', {
            'fullname': '',
            'email': 'not-an-email',
            'phone': '+355 69 123 4567',
            'message': 'Hello',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_contact_message_is_limited_to_5000_characters(self):
        response = self.client.post('/contact/', {
            'fullname': 'Test Visitor',
            'email': 'visitor@example.com',
            'phone': '+355 69 123 4567',
            'message': 'x' * 5001,
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].has_error('message', 'max_length'))
        self.assertEqual(ContactMessage.objects.count(), 0)

    @override_settings(
        CONTACT_NOTIFICATION_EMAIL='sales@example.com',
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    )
    def test_valid_contact_submission_sends_notification_when_configured(self):
        response = self.client.post('/contact/', {
            'fullname': 'Test Visitor',
            'email': 'visitor@example.com',
            'phone': '+355 69 123 4567',
            'message': 'I would like to schedule a visit.',
        })

        self.assertRedirects(response, '/contact/')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['sales@example.com'])
        self.assertIn('visitor@example.com', mail.outbox[0].body)
