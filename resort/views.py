from django.contrib import messages
from django.contrib.staticfiles import finders
from django.http import Http404
from django.shortcuts import redirect, render

from .models import ContactMessage

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
        'plan_ground': 'image/plan-ground.jpg', 'plan_first': 'image/plan-first.jpg', 'plan_second': '',
        'gallery': [], 'features': COMMON_FEATURES,
    },
    {
        'id': 3, 'type': 'type-c', 'name': 'Okazion - Tirane',
        'rooms': '5+1', 'area': 280, 'bedrooms': 5, 'bathrooms': 4, 'floors': 3, 'plot': 600,
        'description': 'A three-floor villa with five bedrooms, designed for larger families who value space and privacy.',
        'image': 'image/villas/type-c.jpg',
        'plan_ground': 'image/plan-ground.jpg', 'plan_first': 'image/plan-first.jpg', 'plan_second': 'image/plan-first.jpg',
        'gallery': [], 'features': COMMON_FEATURES,
    },
    {
        'id': 4, 'type': 'type-d', 'name': 'Vile - lunder',
        'rooms': '6+1', 'area': 320, 'bedrooms': 6, 'bathrooms': 5, 'floors': 3, 'plot': 700,
        'description': 'Our largest villa: six bedrooms over three floors, with premium finishes and a large private plot.',
        'image': 'image/villas/type-d.jpg',
        'plan_ground': 'image/plan-ground.jpg', 'plan_first': 'image/plan-first.jpg', 'plan_second': 'image/plan-first.jpg',
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


def index_view(request):
    return render(request, 'home.html', {'villas': VILLAS[:3]})


def about_view(request):
    return render(request, 'about.html')


def villas_view(request):
    return render(request, 'villas.html', {'villas': VILLAS})


def villa_detail_view(request, pk):
    villa = next((v for v in VILLAS if v['id'] == pk), None)
    if villa is None:
        raise Http404("Villa not found")
    # Nëse galeria nuk është shkruar me dorë, merret automatikisht nga skedarët
    if villa['gallery']:
        gallery = [g if isinstance(g, dict) else {'src': g, 'label': ''} for g in villa['gallery']]
    else:
        gallery = build_gallery(villa['type'])
    villa = {**villa, 'gallery': gallery}
    return render(request, 'villa-detail.html', {'villa': villa})


def gallery_view(request):
    return render(request, 'gallery.html')


def location_view(request):
    return render(request, 'location.html')


def contact_view(request):
    if request.method == 'POST':
        ContactMessage.objects.create(
            fullname=request.POST.get('fullname', '').strip(),
            email=request.POST.get('email', '').strip(),
            phone=request.POST.get('phone', '').strip(),
            message=request.POST.get('message', '').strip(),
        )
        messages.success(request, 'Thank you! Your message has been sent.')
        return redirect('contact')
    return render(request, 'contact.html')