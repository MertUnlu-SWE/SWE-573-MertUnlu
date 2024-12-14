from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class StaticFilesStorage(S3Boto3Storage):
    location = settings.STATICFILES_FOLDER

class MediaFilesStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_FOLDER