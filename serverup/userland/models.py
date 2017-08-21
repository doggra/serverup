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
	credits = models.IntegerField(default=0)
	customers_limit = models.IntegerField(default=1)
	administrator = models.ForeignKey(User, null=True, related_name='resellers')


class Customer(models.Model):
	user = models.OneToOneField(User)
	credits = models.IntegerField(default=0)
	servers_limit = models.IntegerField(default=1)
	reseller = models.ForeignKey(User, null=True, related_name='customers')


class Profile(models.Model):
	uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
	user = models.OneToOneField(User)
	account_type = models.IntegerField(choices=ACCOUNT_TYPES, default=0)


	def __unicode__(self):
		return self.user.username

	@property
	def type(self):
		return self.get_account_type_display()

	def can_add_server(self):
		# If reseller or administrator - no restrictions to add new servers.
		if self.account_type > 0:
			return True
		else:
			mat = self.user.server_set.count() - self.user.customer.servers_limit
			if mat < 0:
				# Return remaining number of available servers
				return -mat
			else:
				return False