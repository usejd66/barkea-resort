"""Responsive copies of the project's static photos.

`python manage.py build_responsive_images` writes WebP copies of every photo in
static/image at several widths (originals are never modified) and records them in
responsive_images.json. Templates then emit a `srcset` so each browser downloads
the size that matches its screen, while the full-quality original stays available
for the gallery lightbox.
"""

import json
from functools import lru_cache
from pathlib import Path

from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.html import format_html

RESPONSIVE_WIDTHS = (480, 800, 1200, 1600, 2400, 3200)
# Full-width hero photos need up to 3200px for large retina screens. Every other photo
# is shown at most ~620 CSS px wide, so 1600px already covers 2x and 3x displays.
HERO_MAX_WIDTH = 3200
DEFAULT_MAX_WIDTH = 1600
OUTPUT_PREFIX = 'image/responsive'
MANIFEST_PATH = Path(__file__).with_name('responsive_images.json')


def max_width_for(static_path):
    name = static_path.rsplit('/', 1)[-1]
    return HERO_MAX_WIDTH if name.startswith('hero-') else DEFAULT_MAX_WIDTH


@lru_cache(maxsize=1)
def load_manifest():
    try:
        return json.loads(MANIFEST_PATH.read_text())
    except FileNotFoundError:
        return {}


def srcset_for(static_path):
    """Return a srcset value for a static photo, or '' if no copies were built."""
    variants = load_manifest().get(static_path, [])
    return ', '.join(
        f'{staticfiles_storage.url(path)} {width}w' for width, path in variants
    )


def responsive_attrs(static_path, sizes):
    """Render ` srcset="…" sizes="…"` for an <img>, or nothing when unavailable."""
    srcset = srcset_for(static_path) if static_path else ''
    if not srcset:
        return ''
    return format_html(' srcset="{}" sizes="{}"', srcset, sizes)
