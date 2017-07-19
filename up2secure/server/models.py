# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

OS_DISTRO = (
	(0, "Debian"),
	(1, "Centos"),
)

STATUS = (
	(0, "UPDATED"),
	(1, "PENDING"),
	(2, "IGNORED"),
)


class Package(models.Model):
	name = models.CharField(max_length=255)


class PackageUpdate(models.Model):
	server = models.ForeignKey('Server', on_delete=models.CASCADE)
	package = models.ForeignKey(Package)
	version = models.CharField(max_length=255, blank=True)
	status = models.IntegerField(default=1, choices=STATUS)


class Server(models.Model):
	user = models.ForeignKey(User)
	os = models.IntegerField(null=True, choices=OS_DISTRO)
	ip = models.GenericIPAddressField(default='127.0.0.1')
	hostname = models.CharField(max_length=255, blank=True)
	status = models.IntegerField(default=0, choices=STATUS)
	public_key = models.TextField(blank=True)
	private_key = models.TextField(blank=True)

	@property
	def show_status(self):
		if self.status == 0:
			return "<span class='badge bg-green'>UPDATED</span>"
		elif self.status == 1:
			count_pending_updates = UpdatePackage.objects.filter(server=self, status=1).count()
			return "<span class='badge bg-orange'>{} PENDING UPDATES</span>"\
																.format(count_pending_updates,)

	@property
	def show_os_icon(self):
		if self.os == 0:
			return "<i class='devicon-debian-plain'></i>"
		elif self.os == 1:
			return "<i class='devicon-redhat-plain'></i>"
		else:
			return "?"

	def __unicode__(self):
		return self.ip


class ServerGroup(models.Model):
	name = models.CharField(max_length=20)
	user = models.ForeignKey(User)
	servers = models.ManyToManyField(Server, blank=True)

	@property
	def count_servers(self):
		return self.servers.count()

	def __unicode__(self):
		return self.name
