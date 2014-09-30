from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# -*- coding: utf-8 -*-

class Document(models.Model):
    myfile = models.FileField(upload_to='mcts/media')
