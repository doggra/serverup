# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView


class Dashboard(TemplateView):
	template_name = "userland/dashboard.html"


class History(TemplateView):
	template_name = "userland/history.html"
	

class Accounting(TemplateView):
	template_name = "userland/accounting.html"
	