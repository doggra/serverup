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
	account_type = models.IntegerField(choices=ACCOUNT_TYPES)

	def __unicode__(self):
		return self.user.username