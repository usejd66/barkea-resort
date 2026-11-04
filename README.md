# Barkea Resort

Website-i i Barkea Resort është ndërtuar me Django, HTML, CSS, JavaScript dhe Bootstrap.

## Nisja lokale

Kërkohet Python dhe pip. Krijo një mjedis virtual dhe instalo varësitë:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Në Windows aktivizo mjedisin me `.venv\Scripts\activate`. Për zhvillim lokal, vendos `DJANGO_DEBUG=True`, pastaj ekzekuto:

```sh
python manage.py migrate
python manage.py runserver
```

Pa `DJANGO_DEBUG=True`, aplikacioni kërkon `DJANGO_SECRET_KEY`. Në prodhim vendos gjithashtu `DJANGO_ALLOWED_HOSTS` si listë hostesh të ndara me presje dhe, kur nevojitet, `DJANGO_CSRF_TRUSTED_ORIGINS` si listë origjinash HTTPS të ndara me presje. Mos përdor vlerën e zhvillimit në prodhim. Pasi hosti të jetë konfiguruar për HTTPS, aktivizo `DJANGO_SECURE_SSL_REDIRECT=True` dhe vendos `DJANGO_HSTS_SECONDS` sipas politikës së hostit.

Mesazhet e kontaktit ruhen në databazë dhe mund të shihen nga admin-i i Django-s. Njoftimi me email është opsional: vendos `CONTACT_NOTIFICATION_EMAIL`, `DJANGO_EMAIL_HOST`, `DJANGO_EMAIL_USER`, `DJANGO_EMAIL_PASSWORD` dhe `DJANGO_DEFAULT_FROM_EMAIL` në mjedisin e hostit; asnjë kredencial nuk duhet ruajtur në Git. Databaza lokale `db.sqlite3` nuk duhet përdorur për të dhëna prodhimi.

## Testet

```sh
python manage.py test
```
