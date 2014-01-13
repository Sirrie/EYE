import requests
from cStringIO import StringIO

from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models, transaction

from django_images.models import Image as BaseImage, Thumbnail
from taggit.managers import TaggableManager
from django.contrib.auth.models import User



class Photo(models.Model):
    description = models.CharField(max_length=200)
    user = models.ForeignKey(User)
    imgurl = models.CharField(max_length=100)
    thumbnail = models.CharField(max_length=100)
    tags = TaggableManager()
   # viewNum = models.IntegerField
    
    def __unicode__(self):
        return self.text

class Comments(models.Model):
    photo = models.ForeignKey(Photo)
    text = models.CharField(max_length=500)
    user = models.ForeignKey(User)

    def as_json(self):
        return dict(
            pid=self.photo.id,
            text=self.text, 
            user=self.user.username)

    def __unicode__(self):
        return self.text

class Like(models.Model):
    photo = models.ForeignKey(Photo)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return self.text