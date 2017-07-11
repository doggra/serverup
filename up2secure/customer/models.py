# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from reseller.models import Reseller


class Customer(models.Model):
	user = models.OneToOneField(User)
	credits = models.IntegerField(default=0)
	servers_limit = models.IntegerField(default=1)
	reseller = models.ForeignKey(Reseller)
