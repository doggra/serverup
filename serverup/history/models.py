# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
# from django.contrib.auth.models import User

EVENT_TYPES = (
	(0, 'SSH Command'),
)


class Event(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)
	server = models.ForeignKey('server.Server', on_delete=models.CASCADE, 
												null=True)
	
	_type = models.IntegerField(default=0, choices=EVENT_TYPES)
	info = models.TextField()
	extra_info = models.CharField(max_length=255, default="")
