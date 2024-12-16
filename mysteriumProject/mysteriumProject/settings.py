"""
Django settings for mysteriumProject project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-etebo%)_nxf1pozgvb1=1$)+5cr#hzb3*#lftdx&eg!%5__4si'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG =  os.getenv("IS_DEVELOPMENT", False)


ALLOWED_HOSTS = [
    'mysterium.onrender.com',
    'www.mysterium.onrender.com',
    'swe-573-mertunlu.onrender.com',
    'django_app', 
    '91.93.225.91/32', 
    '13.53.116.156', 
    '127.0.0.1',
    '172.18.0.2',
    '172.19.0.2', 
    'localhost', 
    '[::1]'
]

CSRF_TRUSTED_ORIGINS = [
    'https://mysterium.onrender.com',
    'https://mysterium-nginx-latest.onrender.com',
    'https://www.mysterium.onrender.com',
    'https://swe-573-mertunlu.onrender.com',
    'http://localhost',
    'http://127.0.0.1:8000',
    'http://localhost:8000/',
    'http://127.0.0.1:8000/'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mysterium',
    'storages',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysteriumProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysteriumProject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',  # AWS RDS SSL Usage
        },
    }
}


AUTHENTICATION_BACKENDS = [
    'mysterium.backends.EmailBackend',  # Adjust this to match your app name
    'django.contrib.auth.backends.ModelBackend',
]

# Password validation

# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Istanbul'

USE_I18N = True

USE_TZ = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Static Files Local
# Static Files
STATIC_URL = '/static/'

# Statik dosyaların toplandığı hedef dizin (collectstatic ile)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Kaynak statik dosyaların bulunduğu dizinler
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Projenizin statik dosyaları buradadır
]

# Media Files Local
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATICFILES_FOLDER = 'static'
MEDIAFILES_FOLDER = 'media'

STORAGES = {
    "staticfiles": {
        "BACKEND": "custom_storages.StaticFilesStorage",
    },
    "default": {
        "BACKEND": "custom_storages.MediaFilesStorage",
    }
}

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'


STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

import mimetypes
mimetypes.add_type("text/css", ".css", True)

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
