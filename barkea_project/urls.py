from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('resort.urls')),
]

# Shërben skedarët e ngarkuar (media) në zhvillim, ose kur hosti nuk mund t'i shërbejë vetë.
if settings.SERVE_MEDIA:
    media_prefix = settings.MEDIA_URL.lstrip('/')
    urlpatterns += [
        re_path(rf'^{media_prefix}(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
