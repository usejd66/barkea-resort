"""Të dhëna që u duhen të gjitha faqeve (menuja, kontakti), të përcaktuara në një vend."""

from django.urls import reverse

# (emri i URL-së, teksti, faqet ku lidhja shfaqet si aktive)
NAV_ITEMS = (
    ('home', 'Home', ('home',)),
    ('about', 'About Us', ('about',)),
    ('villas', 'Villas', ('villas', 'villa_detail')),
    ('gallery', 'Gallery', ('gallery',)),
    ('location', 'Location', ('location',)),
)

SITE_CONTACT = {
    'phone': '+355 69 123 4567',
    'phone_href': '+355691234567',
    'email': 'info@barkearesort.al',
    'address_lines': ('Lundër / Farkë', 'Tirana, Albania'),
}

SOCIAL_LINKS = (
    ('Facebook', 'bi-facebook', '#'),
    ('Instagram', 'bi-instagram', '#'),
    ('LinkedIn', 'bi-linkedin', '#'),
)


def site(request):
    match = getattr(request, 'resolver_match', None)
    current = match.url_name if match else None
    return {
        'nav_items': [
            {
                'label': label,
                'url': reverse(url_name),
                'active': current in active_on,
            }
            for url_name, label, active_on in NAV_ITEMS
        ],
        'contact_page_active': current == 'contact',
        'site_contact': SITE_CONTACT,
        'social_links': [
            {'label': label, 'icon': icon, 'url': url} for label, icon, url in SOCIAL_LINKS
        ],
    }
