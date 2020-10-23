from django.db import models
from django.conf import settings
# Create your models here.

class Article(models.Model):
  title = models.CharField(max_length=64)
  content = models.TextField()
  author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Comment(models.Model):
  article = models.ForeignKey(Article, on_delete=models.CASCADE)
  content = models.TextField()
  author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
