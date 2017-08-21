# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


EVENT_TYPES = (
	(0, 'SSH command sent'),
	(1, 'Server added'),
)


class Event(models.Model):
	datetime = models.DateTimeField(auto_now_add=True)
	server = models.ForeignKey('server.Server', on_delete=models.CASCADE, 
												null=True)
	
	event_type = models.IntegerField(default=0, choices=EVENT_TYPES)
	info = models.TextField(default="")
	extra_info = models.CharField(max_length=255, default="")

	class Meta:
		ordering = ('-datetime',)