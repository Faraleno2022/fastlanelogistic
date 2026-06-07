# Dans helpers/cloudflare/storages.py
from storages.backends.s3boto3 import S3Boto3Storage

class StaticFileStorage(S3Boto3Storage):
    location = 'static'

class MediaFileStorage(S3Boto3Storage):
    location = 'media'