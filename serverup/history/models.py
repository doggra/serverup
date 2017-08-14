# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class EventType(models.Model):
	name = models.CharField(max_length=255)


class Event(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)
	info = models.TextField()
	user = models.ForeignKey(User)
