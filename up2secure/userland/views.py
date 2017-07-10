# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView


class Home(TemplateView):
	template_name = "userland/home.html"


class Servers(TemplateView):
	template_name = "userland/servers.html"


class Updates(TemplateView):
	template_name = "userland/updates.html"
	

class Accounting(TemplateView):
	template_name = "userland/accounting.html"
	