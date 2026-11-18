import logging
from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.mail import EmailMessage
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render

from .forms import ContactRequestForm
from .models import GalleryImage, Villa, VillaType

logger = logging.getLogger(__name__)

CONTACT_SUCCESS_MESSAGE = 'Thank you! Your message has been received.'


def _published_villas():
    return Villa.objects.filter(
        is_published=True,
        villa_type__is_active=True,
    ).select_related('villa_type').prefetch_related('features', 'gallery_images')


def _asset_url(uploaded_image, static_image):
    """Përdor foton e ngarkuar nga admin-i; përndryshe foton statike të projektit."""
    if uploaded_image:
        return uploaded_image.url
    if static_image:
        return staticfiles_storage.url(static_image)
    return ''


def _villa_data(villa):
    data = {
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
    for floor in ('ground', 'first', 'second'):
        url = _asset_url(getattr(villa, f'plan_{floor}'), getattr(villa, f'static_plan_{floor}'))
        data[f'plan_{floor}'] = bool(url)
        data[f'plan_{floor}_url'] = url
    return data


def index_view(request):
    villas = [_villa_data(villa) for villa in _published_villas()[:3]]
    return render(request, 'home.html', {'villas': villas})


def about_view(request):
    return render(request, 'about.html')


def villas_view(request):
    villas = [_villa_data(villa) for villa in _published_villas()]
    villa_types = VillaType.objects.filter(
        is_active=True,
        villas__is_published=True,
    ).distinct()
    return render(request, 'villas.html', {'villas': villas, 'villa_types': villa_types})


def villa_detail_view(request, pk):
    try:
        villa = _published_villas().get(pk=pk)
    except Villa.DoesNotExist as error:
        raise Http404('Villa not found') from error
    return render(request, 'villa-detail.html', {'villa': _villa_data(villa)})


def gallery_view(request):
    # Fotot e një vile shfaqen vetëm kur vila (dhe tipi i saj) është publike.
    images = GalleryImage.objects.filter(
        Q(villa__isnull=True)
        | Q(villa__is_published=True, villa__villa_type__is_active=True),
        is_published=True,
    ).select_related('villa')
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


def _send_contact_notification(contact_message):
    """Njofton ekipin me email. Dështimet logohen, por nuk i shfaqen vizitorit."""
    email = EmailMessage(
        subject='New Barkea Resort contact request',
        body=(
            f'Name: {contact_message.fullname}\n'
            f'Email: {contact_message.email}\n'
            f'Phone: {contact_message.phone}\n\n'
            f'{contact_message.message}'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.CONTACT_NOTIFICATION_EMAIL],
        reply_to=[contact_message.email],
    )
    try:
        sent = email.send(fail_silently=False)
    except (OSError, SMTPException):
        logger.exception('Could not send contact notification email.')
        return
    if not sent:
        logger.error('Contact notification email was not accepted by the email backend.')


def contact_view(request):
    if request.method == 'POST':
        form = ContactRequestForm(request.POST)
        if form.is_valid():
            if form.is_spam():
                # Bot-et marrin të njëjtën përgjigje, por asgjë nuk ruhet.
                logger.info('Discarded contact submission caught by honeypot.')
            else:
                contact_message = form.save()
                if settings.CONTACT_NOTIFICATION_EMAIL:
                    _send_contact_notification(contact_message)
            messages.success(request, CONTACT_SUCCESS_MESSAGE)
            return redirect('contact')
    else:
        form = ContactRequestForm()
    return render(request, 'contact.html', {'form': form})
