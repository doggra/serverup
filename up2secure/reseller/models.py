# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Reseller(models.Model):
	user = models.OneToOneField(User)
	customers_limit = models.IntegerField(default=1)
