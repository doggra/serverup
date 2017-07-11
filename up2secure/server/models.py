# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

SERVER_STATUS = (
	(0, "Up to date"),
	(1, "Not updated"),
)


class Server(models.Model):
	user = models.ForeignKey(User)
	ip = models.GenericIPAddressField(default='127.0.0.1')
	hostname = models.CharField(max_length=255)
	status = models.IntegerField(default=0, choices=SERVER_STATUS)


class ServerGroup(models.Model):
	name = models.CharField(max_length=20)
	user = models.ForeignKey(User)
	servers = models.ManyToManyField(Server, blank=True)

	def __unicode__(self):
		return self.name