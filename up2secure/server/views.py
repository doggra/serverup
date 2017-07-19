# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import join
from django.conf import settings
from django.shortcuts import render
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect

from django.views.generic import TemplateView
from django.views.generic.edit import DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Server, ServerGroup, Update


@method_decorator(login_required, name='dispatch')
class ServersControlPanelView(TemplateView):
	template_name = "server/servers.html"

	def get_context_data(self, **kwargs):
		context = super(ServersControlPanelView, self).get_context_data(**kwargs)
		context['servers'] = Server.objects.filter(user=self.request.user)
		context['server_groups'] = ServerGroup.objects.filter(user=self.request.user)

		site_address = self.request.get_host()
		context['install_script'] = "wget -O - http://{}/install/ | bash".format(site_address)
		return context


@method_decorator(login_required, name='dispatch')
class ServerDetails(DetailView):
	model = Server


@method_decorator(login_required, name='dispatch')
class ServerGroupView(DetailView):
	model = ServerGroup


@method_decorator(login_required, name='dispatch')
class UpdatesListView(ListView):
	model = Update


@method_decorator(login_required, name='dispatch')
class DeleteGroupView(DeleteView):
	model = ServerGroup
	success_url = reverse_lazy('servers')


@login_required
def add_group(request):
	if request.method == 'POST':
		ServerGroup.objects.get_or_create(user=request.user, name=request.POST['name'])
	return HttpResponseRedirect(reverse('servers'))


def install_server(request):
	install_script = ""
	with open(join(settings.PROJECT_ROOT, 'install.sh'), 'r') as f:
		install_script = f.read()
	return HttpResponse(install_script)
