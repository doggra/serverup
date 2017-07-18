# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


ACCOUNT_TYPES = (
	(0, "Customer"),
	(1, "Reseller"),
	(2, "Administrator"),
)


class Profile(models.Model):
	user = models.OneToOneField(User)
	credits = models.IntegerField(default=0)
	server_limit = models.IntegerField(default=1)
	account_type = models.IntegerField(choices=ACCOUNT_TYPES)

	def __unicode__(self):
		return self.user.username

	@property
	def type(self):
		return self.get_account_type_display()