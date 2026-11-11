import logging
from smtplib import SMTPException

from django.contrib import messages
from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import redirect, render

from .forms import ContactRequestForm
from .models import GalleryImage, Villa, VillaType

logger = logging.getLogger(__name__)

# Karakteristikat e përbashkëta (mund t'i ndryshosh për secilën vilë)
COMMON_FEATURES = [
    {'icon': 'bi-thermometer-half', 'text': 'Advanced thermal insulation'},
    {'icon': 'bi-window', 'text': 'Energy-efficient windows'},
    {'icon': 'bi-wind', 'text': 'Modern heating & cooling'},
    {'icon': 'bi-shield-lock', 'text': 'Gated, secure community'},
    {'icon': 'bi-car-front', 'text': 'Private parking'},
    {'icon': 'bi-flower1', 'text': 'Garden area'},
]

VILLAS = [
    {
        'id': 1, 'type': 'type-a', 'name': 'Vile ne shitje - Tirane',
        'rooms': '3+1', 'area': 180, 'bedrooms': 3, 'bathrooms': 3, 'floors': 2, 'plot': 400,
        'description': 'A compact and elegant villa, ideal for young families who want modern living close to the city.',
        'image': 'image/villas/type-a.png',
        'plan_ground': 'image/plan-ground.png', 'plan_first': 'image/plan-first.png', 'plan_second': '',
        'gallery': [], 'features': COMMON_FEATURES,
    },
    {
        'id': 2, 'type': 'type-b', 'name': 'Vile ne perfundim',
        'rooms': '4+1', 'area': 220, 'bedrooms': 4, 'bathrooms': 3, 'floors': 2, 'plot': 500,
        'description': 'A spacious family villa with generous living areas and a large veranda overlooking the garden.',
        'image': 'image/villas/type-b.png',
        'plan_ground': 'image/plan-ground.png', 'plan_first': 'image/plan-first.png', 'plan_second': '',
        'gallery': [], 'features': COMMON_FEATURES,
    },
    {
        'id': 3, 'type': 'type-c', 'name': 'Okazion - Tirane',
        'rooms': '5+1', 'area': 280, 'bedrooms': 5, 'bathrooms': 4, 'floors': 3, 'plot': 600,
        'description': 'A three-floor villa with five bedrooms, designed for larger families who value space and privacy.',
        'image': 'image/villas/type-c.jpg',
        'plan_ground': 'image/plan-ground.png', 'plan_first': 'image/plan-first.png', 'plan_second': '',
        'gallery': [], 'features': COMMON_FEATURES,
    },
    {
        'id': 4, 'type': 'type-d', 'name': 'Vile - lunder',
        'rooms': '6+1', 'area': 320, 'bedrooms': 6, 'bathrooms': 5, 'floors': 3, 'plot': 700,
        'description': 'Our largest villa: six bedrooms over three floors, with premium finishes and a large private plot.',
        'image': 'image/villas/type-d.jpg',
        'plan_ground': 'image/plan-ground.png', 'plan_first': 'image/plan-first.png', 'plan_second': '',
        'gallery': [], 'features': COMMON_FEATURES,
    },
]


# Dhomat që kërkohen automatikisht, me etiketën që shfaqet te galeria
GALLERY_ROOMS = [
    ('living', 'Living Room'),
    ('kitchen', 'Kitchen'),
    ('bedroom', 'Bedroom'),
    ('bedroom-2', 'Bedroom 2'),
    ('bedroom-3', 'Bedroom 3'),
    ('bedroom-4', 'Bedroom 4'),
    ('bathroom', 'Bathroom'),
    ('bathroom-2', 'Bathroom 2'),
    ('terrace', 'Terrace'),
    ('garden', 'Garden'),
]
GALLERY_EXTS = ('jpg', 'jpeg', 'png', 'webp')


def _find(base):
    for ext in GALLERY_EXTS:
        path = f'{base}.{ext}'
        if finders.find(path):
            return path
    return None


def build_gallery(villa_type, max_extra=8):
    """Gjen automatikisht fotot e brendshme të vilës te static/image/villas/.

    Emrat e pritur, p.sh. për vilën type-a:
      type-a-living.jpg, type-a-kitchen.jpg, type-a-bedroom.jpg,
      type-a-bedroom-2.jpg, type-a-bathroom.jpg, type-a-terrace.jpg ...
    Edhe emra me numra: type-a-1.jpg, type-a-2.jpg ...
    Merren vetëm skedarët që ekzistojnë, pra nuk dalin foto të thyera.
    """
    items = []
    for key, label in GALLERY_ROOMS:
        path = _find(f'image/villas/{villa_type}-{key}')
        if path:
            items.append({'src': path, 'label': label})
    for n in range(1, max_extra + 1):
        path = _find(f'image/villas/{villa_type}-{n}')
        if path:
            items.append({'src': path, 'label': ''})
    return items


def _published_villas():
    return Villa.objects.filter(
        is_published=True,
        villa_type__is_active=True,
    ).select_related('villa_type').prefetch_related('features', 'gallery_images')


def _asset_url(uploaded_image, static_image):
    if uploaded_image:
        return uploaded_image.url
    if static_image:
        return staticfiles_storage.url(static_image)
    return ''


def _database_villa_data(villa):
    return {
        'id': villa.pk,
        'type': villa.villa_type.slug,
        'name': villa.name,
        'rooms': villa.rooms,
        'area': villa.area,
        'bedrooms': villa.bedrooms,
        'bathrooms': villa.bathrooms,
        'floors': villa.floors,
        'plot': villa.plot,
        'description': villa.description,
        'image_url': _asset_url(villa.image, villa.static_image),
        'plan_ground': bool(villa.plan_ground or villa.static_plan_ground),
        'plan_ground_url': _asset_url(villa.plan_ground, villa.static_plan_ground),
        'plan_first': bool(villa.plan_first or villa.static_plan_first),
        'plan_first_url': _asset_url(villa.plan_first, villa.static_plan_first),
        'plan_second': bool(villa.plan_second or villa.static_plan_second),
        'plan_second_url': _asset_url(villa.plan_second, villa.static_plan_second),
        'gallery': [
            {
                'src': _asset_url(image.image, image.static_image),
                'label': image.caption,
            }
            for image in villa.gallery_images.all()
            if image.is_published
        ],
        'features': [
            {'icon': feature.icon, 'text': feature.name}
            for feature in villa.features.all()
        ],
    }


def _static_villa_data(villa):
    data = {**villa}
    data['image_url'] = staticfiles_storage.url(villa['image'])
    for floor in ('ground', 'first', 'second'):
        path = villa[f'plan_{floor}']
        data[f'plan_{floor}_url'] = staticfiles_storage.url(path) if path else ''
    return data


def _public_villas():
    if Villa.objects.exists():
        return [_database_villa_data(villa) for villa in _published_villas()]
    return [_static_villa_data(villa) for villa in VILLAS]


def index_view(request):
    return render(request, 'home.html', {'villas': _public_villas()[:3]})


def about_view(request):
    return render(request, 'about.html')


def villas_view(request):
    villas = _public_villas()
    if Villa.objects.exists():
        villa_types = VillaType.objects.filter(
            is_active=True,
            villas__is_published=True,
        ).distinct()
    else:
        villa_types = [
            {'slug': villa['type'], 'name': villa['type'].replace('type-', 'Type ').title()}
            for villa in VILLAS
        ]
    return render(request, 'villas.html', {'villas': villas, 'villa_types': villa_types})


def villa_detail_view(request, pk):
    if Villa.objects.exists():
        try:
            villa = _published_villas().get(pk=pk)
        except Villa.DoesNotExist as error:
            raise Http404("Villa not found") from error
        return render(request, 'villa-detail.html', {'villa': _database_villa_data(villa)})

    villa = next((item for item in VILLAS if item['id'] == pk), None)
    if villa is None:
        raise Http404('Villa not found')
    # Nëse galeria nuk është shkruar me dorë, merret automatikisht nga skedarët
    if villa['gallery']:
        gallery = [g if isinstance(g, dict) else {'src': g, 'label': ''} for g in villa['gallery']]
    else:
        gallery = build_gallery(villa['type'])
    villa = _static_villa_data({**villa, 'gallery': gallery})
    villa['gallery'] = [
        {**item, 'src': staticfiles_storage.url(item['src'])}
        for item in gallery
    ]
    return render(request, 'villa-detail.html', {'villa': villa})


def gallery_view(request):
    images = GalleryImage.objects.filter(is_published=True).select_related('villa')
    gallery_images = [
        {
            'image_url': _asset_url(image.image, image.static_image),
            'alt_text': image.alt_text,
            'caption': image.caption or image.alt_text,
            'category': image.category,
        }
        for image in images
    ]
    return render(request, 'gallery.html', {'gallery_images': gallery_images})


def location_view(request):
    return render(request, 'location.html')


def contact_view(request):
    if request.method == 'POST':
        form = ContactRequestForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            if settings.CONTACT_NOTIFICATION_EMAIL:
                try:
                    sent = send_mail(
                        subject='New Barkea Resort contact request',
                        message=(
                            f'Name: {contact_message.fullname}\n'
                            f'Email: {contact_message.email}\n'
                            f'Phone: {contact_message.phone}\n\n'
                            f'{contact_message.message}'
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[settings.CONTACT_NOTIFICATION_EMAIL],
                        fail_silently=False,
                    )
                except (OSError, SMTPException):
                    logger.exception('Could not send contact notification email.')
                    messages.warning(
                        request,
                        'Your message was saved, but we could not send an email notification.',
                    )
                else:
                    if sent:
                        messages.success(request, 'Thank you! Your message has been received.')
                    else:
                        logger.error('Contact notification email was not accepted by the email backend.')
                        messages.warning(
                            request,
                            'Your message was saved, but we could not send an email notification.',
                        )
            else:
                messages.success(request, 'Thank you! Your message has been received.')
            return redirect('contact')
    else:
        form = ContactRequestForm()
    return render(request, 'contact.html', {'form': form})
