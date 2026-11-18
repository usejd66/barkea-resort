from unittest import mock

from django.core import mail
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.template import Context, Template
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContactRequest, Feature, GalleryImage, Villa, VillaType


class PublicPagesTests(TestCase):
    def test_public_pages_render(self):
        for url in ('/', '/about/', '/villas/', '/gallery/', '/location/', '/contact/'):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_unknown_villa_returns_404(self):
        response = self.client.get('/villas/999/')
        self.assertEqual(response.status_code, 404)

    def test_gallery_has_accessible_filters_lightbox_and_lazy_thumbnails(self):
        response = self.client.get('/gallery/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="gallery-lightbox"')
        self.assertContains(response, 'aria-pressed="true"')
        self.assertContains(response, 'data-filter="exterior"')
        self.assertContains(response, 'data-filter="interior"')
        self.assertContains(response, 'data-filter="amenities"')
        self.assertContains(response, 'loading="lazy"')
        self.assertContains(response, 'decoding="async"')
        self.assertEqual(response.content.count(b'data-gallery-item'), 14)

    def test_villa_pages_do_not_render_missing_floor_plan_urls(self):
        for villa in Villa.objects.all():
            with self.subTest(villa=villa.slug):
                response = self.client.get(f'/villas/{villa.slug}/')
                self.assertEqual(response.status_code, 200)
                self.assertNotContains(response, 'src="/static/"')

    def test_villa_links_use_slugs(self):
        response = self.client.get('/villas/')

        self.assertContains(response, 'href="/villas/vile-ne-shitje-tirane/"')
        self.assertNotContains(response, 'href="/villas/1/"')

    def test_old_numeric_villa_urls_redirect_permanently_to_slug(self):
        villa = Villa.objects.get(slug='vile-ne-shitje-tirane')

        response = self.client.get(f'/villas/{villa.pk}/')

        self.assertRedirects(
            response, '/villas/vile-ne-shitje-tirane/', status_code=301,
        )

    def test_unknown_villa_slug_returns_404(self):
        response = self.client.get('/villas/no-such-villa/')
        self.assertEqual(response.status_code, 404)


class ContactRequestTests(TestCase):
    def test_contact_form_loads_client_validation_and_accessible_required_fields(self):
        response = self.client.get('/contact/')
        html = response.content.decode()

        self.assertContains(response, 'id="contact-form"')
        self.assertContains(response, 'class="toast contact-form-summary w-100"')
        self.assertContains(response, 'id="contact-form-error-list"')
        self.assertContains(response, 'data-bs-autohide="true"')
        self.assertContains(response, 'data-bs-delay="8000"')
        self.assertContains(response, "We couldn't send your request. Please check:")
        self.assertContains(response, 'src="/static/js/form-validation.js"')
        self.assertContains(response, 'href="#id_fullname"')
        self.assertContains(response, 'minlength="10"')
        for field in ('fullname', 'email', 'phone', 'message'):
            with self.subTest(field=field):
                self.assertRegex(
                    html,
                    rf'<(?:input|textarea)\b(?=[^>]*id="id_{field}")(?=[^>]*\brequired\b)[^>]*>',
                )
                self.assertContains(response, f'id="{field}-feedback"')
                self.assertContains(response, f'aria-describedby="{field}-feedback {field}-server-errors"')

    def test_contact_form_validation_script_is_loaded_only_on_contact_page(self):
        response = self.client.get('/')

        self.assertNotContains(response, 'form-validation.js')

    def test_valid_contact_submission_is_saved(self):
        response = self.client.post('/contact/', {
            'fullname': 'Test Visitor',
            'email': 'visitor@example.com',
            'phone': '+355 69 123 4567',
            'message': 'I would like to schedule a visit.',
        })

        self.assertRedirects(response, '/contact/')
        self.assertEqual(ContactRequest.objects.count(), 1)
        self.assertEqual(ContactRequest.objects.get().email, 'visitor@example.com')
        self.assertEqual(ContactRequest.objects.get().status, ContactRequest.Status.NEW)

    def test_contact_name_with_numbers_is_rejected_by_server(self):
        response = self.client.post('/contact/', {
            'fullname': 'Test Visitor 123',
            'email': 'visitor@example.com',
            'phone': '+355 69 123 4567',
            'message': 'I would like to schedule a visit.',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].has_error('fullname', 'invalid_name'))
        self.assertEqual(ContactRequest.objects.count(), 0)

    def test_contact_name_accepts_accented_and_hyphenated_names(self):
        response = self.client.post('/contact/', {
            'fullname': 'Élodie Martin-Smith',
            'email': 'visitor@example.com',
            'phone': '+355 69 123 4567',
            'message': 'I would like to schedule a visit.',
        })

        self.assertRedirects(response, '/contact/')
        self.assertEqual(ContactRequest.objects.get().fullname, 'Élodie Martin-Smith')

    def test_short_contact_message_is_rejected_by_server(self):
        response = self.client.post('/contact/', {
            'fullname': 'Test Visitor',
            'email': 'visitor@example.com',
            'phone': '+355 69 123 4567',
            'message': 'dghbdvdfd',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].has_error('message', 'min_length'))
        self.assertEqual(ContactRequest.objects.count(), 0)

    def test_contact_success_uses_auto_dismissing_toast(self):
        response = self.client.post('/contact/', {
            'fullname': 'Test Visitor',
            'email': 'visitor@example.com',
            'phone': '+355 69 123 4567',
            'message': 'I would like to schedule a visit.',
        }, follow=True)

        self.assertContains(response, 'site-toast-success')
        self.assertContains(response, 'data-bs-autohide="true"')
        self.assertContains(response, 'data-bs-delay="5000"')
        self.assertContains(response, 'Thank you! Your message has been received.')

    def test_invalid_contact_submission_is_not_saved(self):
        response = self.client.post('/contact/', {
            'fullname': '',
            'email': 'not-an-email',
            'phone': '+355 69 123 4567',
            'message': 'Hello',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(ContactRequest.objects.count(), 0)

    def test_contact_message_is_limited_to_5000_characters(self):
        response = self.client.post('/contact/', {
            'fullname': 'Test Visitor',
            'email': 'visitor@example.com',
            'phone': '+355 69 123 4567',
            'message': 'x' * 5001,
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].has_error('message', 'max_length'))
        self.assertEqual(ContactRequest.objects.count(), 0)

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
        self.assertEqual(mail.outbox[0].reply_to, ['visitor@example.com'])

    def test_invalid_phone_is_rejected_by_server(self):
        for phone in ('call me maybe', '12345', '+355 69 123 4567 8901 23'):
            with self.subTest(phone=phone):
                response = self.client.post('/contact/', {
                    'fullname': 'Test Visitor',
                    'email': 'visitor@example.com',
                    'phone': phone,
                    'message': 'I would like to schedule a visit.',
                })
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['form'].has_error('phone', 'invalid_phone'))
        self.assertEqual(ContactRequest.objects.count(), 0)

    def test_honeypot_submission_is_discarded_silently(self):
        with self.assertLogs('resort.views', level='INFO'):
            response = self.client.post('/contact/', {
                'fullname': 'Test Visitor',
                'email': 'bot@example.com',
                'phone': '+355 69 123 4567',
                'message': 'Buy cheap things at my website.',
                'website': 'https://spam.example.com',
            }, follow=True)

        self.assertContains(response, 'Thank you! Your message has been received.')
        self.assertEqual(ContactRequest.objects.count(), 0)

    @override_settings(CONTACT_NOTIFICATION_EMAIL='sales@example.com')
    def test_email_failure_is_not_shown_to_visitor(self):
        with mock.patch('resort.views.EmailMessage.send', side_effect=OSError('SMTP down')):
            with self.assertLogs('resort.views', level='ERROR'):
                response = self.client.post('/contact/', {
                    'fullname': 'Test Visitor',
                    'email': 'visitor@example.com',
                    'phone': '+355 69 123 4567',
                    'message': 'I would like to schedule a visit.',
                }, follow=True)

        self.assertEqual(ContactRequest.objects.count(), 1)
        self.assertContains(response, 'Thank you! Your message has been received.')
        self.assertNotContains(response, 'could not send an email notification')


class ResortContentTests(TestCase):
    def test_existing_villas_features_and_gallery_are_preloaded(self):
        self.assertEqual(Villa.objects.count(), 4)
        self.assertEqual(VillaType.objects.count(), 4)
        self.assertEqual(Feature.objects.count(), 6)
        self.assertEqual(GalleryImage.objects.count(), 14)
        self.assertEqual(Villa.objects.filter(is_published=True).count(), 4)
        first_villa = Villa.objects.get(slug='vile-ne-shitje-tirane')
        self.assertEqual(first_villa.features.count(), 6)
        self.assertEqual(first_villa.static_image, 'image/villas/type-a.png')
        self.assertTrue(finders.find(first_villa.static_image))
        self.assertTrue(all(finders.find(image.static_image) for image in GalleryImage.objects.all()))

    def test_villa_features_and_gallery_images_are_linked(self):
        villa_type = VillaType.objects.create(name='Test Type')
        feature = Feature.objects.create(name='Test Feature')
        villa = Villa.objects.create(
            name='Garden Villa',
            villa_type=villa_type,
            rooms='3+1',
            area=180,
            bedrooms=3,
            bathrooms=3,
            floors=2,
            plot=400,
            description='A modern family villa.',
            image='villas/garden-villa.jpg',
        )
        villa.features.add(feature)
        gallery_image = GalleryImage.objects.create(
            villa=villa,
            image='gallery/garden-villa.jpg',
            alt_text='Garden Villa exterior',
            category=GalleryImage.Category.EXTERIOR,
        )

        self.assertEqual(villa.slug, 'garden-villa')
        self.assertEqual(villa.villa_type.villas.get(), villa)
        self.assertEqual(villa.features.get(), feature)
        self.assertEqual(gallery_image.villa, villa)
        self.assertEqual(villa.gallery_images.get(), gallery_image)

    def test_published_database_content_is_rendered_on_public_pages(self):
        villa_type = VillaType.objects.create(name='Garden Type')
        villa = Villa.objects.create(
            name='Garden Villa',
            villa_type=villa_type,
            rooms='3+1',
            area=180,
            bedrooms=3,
            bathrooms=3,
            floors=2,
            plot=400,
            description='A modern family villa.',
            image='villas/garden-villa.jpg',
            is_published=True,
        )
        gallery_image = GalleryImage.objects.create(
            villa=villa,
            image='gallery/garden-villa.jpg',
            alt_text='Garden Villa exterior',
            category=GalleryImage.Category.EXTERIOR,
        )

        home_response = self.client.get('/')
        villas_response = self.client.get('/villas/')
        detail_response = self.client.get(f'/villas/{villa.slug}/')
        gallery_response = self.client.get('/gallery/')

        self.assertContains(home_response, 'Garden Villa')
        self.assertContains(villas_response, 'value="garden-type">Garden Type')
        self.assertContains(detail_response, '/media/villas/garden-villa.jpg')
        self.assertContains(detail_response, '/media/gallery/garden-villa.jpg')
        self.assertContains(gallery_response, f'data-gallery-full="{gallery_image.image.url}"')
        self.assertEqual(gallery_response.content.count(b'data-gallery-item'), 15)

    def test_unpublishing_all_villas_does_not_fall_back_to_hardcoded_villas(self):
        Villa.objects.update(is_published=False)

        response = self.client.get('/villas/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['villas'], [])
        self.assertEqual(self.client.get('/villas/1/').status_code, 404)
        self.assertEqual(self.client.get('/villas/vile-ne-shitje-tirane/').status_code, 404)

    def test_numeric_slug_is_served_instead_of_redirecting(self):
        villa_type = VillaType.objects.create(name='Year Type')
        villa = Villa.objects.create(
            name='2025',
            villa_type=villa_type,
            rooms='3+1',
            area=180,
            bedrooms=3,
            bathrooms=3,
            floors=2,
            plot=400,
            description='A villa with a numeric name.',
            is_published=True,
        )

        response = self.client.get('/villas/2025/')

        self.assertEqual(villa.slug, '2025')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A villa with a numeric name.')

    def test_gallery_hides_images_of_unpublished_villas(self):
        villa_type = VillaType.objects.create(name='Hidden Type')
        villa = Villa.objects.create(
            name='Hidden Villa',
            villa_type=villa_type,
            rooms='3+1',
            area=180,
            bedrooms=3,
            bathrooms=3,
            floors=2,
            plot=400,
            description='Not yet public.',
            is_published=False,
        )
        GalleryImage.objects.create(
            villa=villa,
            image='gallery/hidden-villa.jpg',
            alt_text='Hidden Villa exterior',
            category=GalleryImage.Category.EXTERIOR,
        )
        GalleryImage.objects.create(
            image='gallery/resort-pool.jpg',
            alt_text='Resort pool',
            category=GalleryImage.Category.AMENITIES,
        )

        response = self.client.get('/gallery/')

        self.assertNotContains(response, 'hidden-villa.jpg')
        self.assertContains(response, 'resort-pool.jpg')

    def test_content_and_contact_models_are_available_in_admin(self):
        user_model = get_user_model()
        user_model.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='test-pass',
        )
        self.client.login(username='admin', password='test-pass')

        for model in (VillaType, Feature, Villa, GalleryImage, ContactRequest):
            with self.subTest(model=model.__name__):
                changelist_url = reverse(f'admin:resort_{model._meta.model_name}_changelist')
                response = self.client.get(changelist_url)
                self.assertEqual(response.status_code, 200)


class ResponsiveImageTests(TestCase):
    def test_hero_offers_webp_sizes_and_keeps_original_as_fallback(self):
        response = self.client.get('/')
        html = response.content.decode()

        self.assertIn('src="/static/image/hero-home.jpg"', html)
        self.assertIn('/static/image/responsive/hero-home-800.webp 800w', html)
        # Në telefon fotoja mbush lartësinë e ekranit, ndaj kërkon kopje më të gjerë.
        self.assertIn('sizes="(max-width: 991.98px) and (orientation: portrait) 145vh, 100vw"', html)

    def test_every_listed_copy_exists(self):
        from .images import load_manifest

        manifest = load_manifest()
        self.assertIn('image/hero-home.jpg', manifest)
        for source, variants in manifest.items():
            with self.subTest(source=source):
                self.assertTrue(finders.find(source))
                for _width, path in variants:
                    self.assertTrue(finders.find(path), path)

    def test_below_the_fold_images_are_lazy_loaded(self):
        response = self.client.get('/')
        self.assertRegex(
            response.content.decode(),
            r'<img src="/static/image/gallery/render-1.jpg"[^>]*loading="lazy"',
        )

    def test_gallery_lightbox_still_uses_full_quality_original(self):
        response = self.client.get('/gallery/')
        self.assertContains(response, 'data-gallery-full="/static/image/villas/type-a-kitchen.jpg"')

    def test_tag_renders_nothing_for_uploaded_or_unknown_images(self):
        template = Template("{% load responsive %}<img{% responsive path '100vw' %}>")
        for path in ('', 'image/not-built.jpg'):
            with self.subTest(path=path):
                self.assertEqual(template.render(Context({'path': path})), '<img>')
