# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


@method_decorator(login_required, name='dispatch')
class ServerListView(TemplateView):
	template_name = "server/servers.html"


@method_decorator(login_required, name='dispatch')
class ServerGroup(TemplateView):
	template_name = "server/server_group.html"