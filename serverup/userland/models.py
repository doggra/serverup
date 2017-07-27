# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid
from django.db import models
from django.contrib.auth.models import User


ACCOUNT_TYPES = (
	(0, "Customer"),
	(1, "Reseller"),
	(2, "Administrator"),
)


class Reseller(models.Model):
	user = models.OneToOneField(User)
	customers_limit = models.IntegerField(default=1)


class Customer(models.Model):
	user = models.OneToOneField(User)
	credits = models.IntegerField(default=0)
	servers_limit = models.IntegerField(default=1)
	reseller = models.ForeignKey(Reseller, blank=True)


class Profile(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
	user = models.OneToOneField(User)
	credits = models.IntegerField(default=0)
	server_limit = models.IntegerField(default=0)
	account_type = models.IntegerField(choices=ACCOUNT_TYPES, default=0)


	def __unicode__(self):
		return self.user.username

	@property
	def type(self):
		return self.get_account_type_display()

	def can_add_server(self):
		if self.server_limit > 0:
			print(self.user.server_set.count(), self.server_limit)
			mat = self.user.server_set.count() - self.server_limit
			if mat < 0:
				# Return remaining number of available servers
				return -mat
			else:
				return False
		else:
			# server_limit == 0 == unlimited servers.
			return True