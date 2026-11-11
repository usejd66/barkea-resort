from django.contrib import admin
from .models import ContactRequest, Feature, GalleryImage, Villa, VillaType


@admin.register(VillaType)
class VillaTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'display_order')
    list_editable = ('display_order',)
    search_fields = ('name', 'description')


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 0


@admin.register(Villa)
class VillaAdmin(admin.ModelAdmin):
    list_display = ('name', 'villa_type', 'rooms', 'area', 'is_published', 'display_order')
    list_editable = ('is_published', 'display_order')
    list_filter = ('villa_type', 'is_published')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug', 'description')
    filter_horizontal = ('features',)
    inlines = (GalleryImageInline,)
    list_select_related = ('villa_type',)
    readonly_fields = ('static_image', 'static_plan_ground', 'static_plan_first', 'static_plan_second')


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'villa', 'category', 'is_published', 'display_order', 'created_at')
    list_editable = ('is_published', 'display_order')
    list_filter = ('category', 'is_published')
    search_fields = ('caption', 'alt_text', 'villa__name')
    list_select_related = ('villa',)
    date_hierarchy = 'created_at'
    readonly_fields = ('static_image',)


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'email', 'phone', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('fullname', 'email', 'phone', 'message')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'