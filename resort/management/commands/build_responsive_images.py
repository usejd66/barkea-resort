import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageOps

from resort.images import (
    MANIFEST_PATH,
    OUTPUT_PREFIX,
    RESPONSIVE_WIDTHS,
    load_manifest,
    max_width_for,
)

SOURCE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
# Folders that already hold derived images.
SKIP_DIRS = {'responsive', 'thumbnails'}
# High quality: at the delivered resolution the difference from the original is not visible.
WEBP_QUALITY = 88


class Command(BaseCommand):
    help = (
        'Create WebP copies of static photos at several widths for srcset. '
        'Originals are left untouched.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true', help='Rebuild copies even if they are up to date.',
        )

    def handle(self, *args, force=False, **options):
        static_root = Path(settings.STATICFILES_DIRS[0])
        image_root = static_root / 'image'
        output_root = static_root / OUTPUT_PREFIX
        output_root.mkdir(parents=True, exist_ok=True)

        manifest = {}
        built = skipped = 0
        for source in sorted(image_root.rglob('*')):
            relative = source.relative_to(image_root)
            if (
                source.suffix.lower() not in SOURCE_EXTENSIONS
                or SKIP_DIRS.intersection(relative.parts[:-1])
            ):
                continue

            static_path = f'image/{relative.as_posix()}'
            # Floor plans contain fine lines and text, so keep them pixel-exact.
            lossless = source.stem.startswith('plan-')
            with Image.open(source) as opened:
                image = ImageOps.exif_transpose(opened)
                icc_profile = opened.info.get('icc_profile')
                cap = max_width_for(static_path)
                widths = [w for w in RESPONSIVE_WIDTHS if w <= cap and w < image.width]
                # Smaller sources (e.g. 1519px PNGs) also get a copy at their own width.
                if image.width < cap:
                    widths.append(image.width)

                variants = []
                for width in widths:
                    name = f'{relative.with_suffix("").as_posix().replace("/", "--")}-{width}.webp'
                    target = output_root / name
                    variants.append([width, f'{OUTPUT_PREFIX}/{name}'])
                    if (
                        not force
                        and target.exists()
                        and target.stat().st_mtime >= source.stat().st_mtime
                    ):
                        skipped += 1
                        continue

                    height = round(image.height * width / image.width)
                    resized = image if width == image.width else image.resize(
                        (width, height), Image.Resampling.LANCZOS,
                    )
                    if resized.mode not in ('RGB', 'RGBA'):
                        resized = resized.convert('RGBA' if 'A' in resized.getbands() else 'RGB')
                    save_options = {'method': 6}
                    if lossless:
                        save_options['lossless'] = True
                    else:
                        save_options['quality'] = WEBP_QUALITY
                    if icc_profile:
                        save_options['icc_profile'] = icc_profile
                    resized.save(target, 'WEBP', **save_options)
                    built += 1
            manifest[static_path] = variants

        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
        load_manifest.cache_clear()
        self.stdout.write(self.style.SUCCESS(
            f'{len(manifest)} photos: {built} copies written, {skipped} already up to date.'
        ))
