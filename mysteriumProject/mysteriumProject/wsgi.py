"""
WSGI config for mysteriumProject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.conf import settings
from whitenoise import WhiteNoise
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysteriumProject.settings')

application = get_wsgi_application()
#application = WhiteNoise(application, root=settings.MEDIA_ROOT, prefix=settings.MEDIA_URL, autorefresh=True)
