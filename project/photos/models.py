from django.contrib.auth.models import User
from django.db import models


class PhotoUpload(models.Model):
    user = models.ForeignKey(User, related_name='photo_uploads', on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
