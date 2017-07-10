# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


SERVER_STATUS = (
	(0, "Up to date"),
	(1, "Not updated"),
)


class Server(models.Model):
	ip = models.GenericIPAddressField(default='127.0.0.1')
	hostname = models.CharField(max_length=255)
	status = models.IntegerField(default=0, choices=SERVER_STATUS)