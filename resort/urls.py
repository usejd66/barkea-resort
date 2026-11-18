from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('villas/', views.villas_view, name='villas'),
    # Adresat e vjetra me numër (/villas/1/) ridrejtohen te adresa me emër.
    path('villas/<int:pk>/', views.villa_legacy_redirect_view, name='villa_detail_legacy'),
    path('villas/<slug:slug>/', views.villa_detail_view, name='villa_detail'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('location/', views.location_view, name='location'),
    path('contact/', views.contact_view, name='contact'),
]