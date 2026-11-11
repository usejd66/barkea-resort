from django.db import models
from django.utils.text import slugify


class VillaType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('display_order', 'name')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Feature(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.CharField(max_length=255, blank=True)
    icon = models.CharField(max_length=80, blank=True)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ('display_order', 'name')

    def __str__(self):
        return self.name


class Villa(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    villa_type = models.ForeignKey(
        VillaType,
        on_delete=models.PROTECT,
        related_name='villas',
    )
    rooms = models.CharField(max_length=20)
    area = models.PositiveIntegerField(help_text='Living area in square metres.')
    bedrooms = models.PositiveSmallIntegerField()
    bathrooms = models.PositiveSmallIntegerField()
    floors = models.PositiveSmallIntegerField()
    plot = models.PositiveIntegerField(help_text='Plot area in square metres.')
    description = models.TextField()
    image = models.ImageField(upload_to='villas/')
    plan_ground = models.ImageField(upload_to='villa-plans/', blank=True)
    plan_first = models.ImageField(upload_to='villa-plans/', blank=True)
    plan_second = models.ImageField(upload_to='villa-plans/', blank=True)
    features = models.ManyToManyField(Feature, related_name='villas', blank=True)
    is_published = models.BooleanField(default=False)
    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ('display_order', 'name')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class GalleryImage(models.Model):
    class Category(models.TextChoices):
        EXTERIOR = 'exterior', 'Exterior'
        INTERIOR = 'interior', 'Interior'
        AMENITIES = 'amenities', 'Amenities'

    villa = models.ForeignKey(
        Villa,
        on_delete=models.SET_NULL,
        related_name='gallery_images',
        blank=True,
        null=True,
    )
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=160, blank=True)
    alt_text = models.CharField(max_length=160)
    category = models.CharField(max_length=20, choices=Category.choices)
    display_order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('display_order', '-created_at')

    def __str__(self):
        return self.caption or self.alt_text


class ContactRequest(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        CONTACTED = 'contacted', 'Contacted'
        RESOLVED = 'resolved', 'Resolved'

    fullname = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    message = models.TextField()
    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.NEW,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.fullname} ({self.email})'
