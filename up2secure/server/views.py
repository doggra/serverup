# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from os.path import join
from fabric.api import run
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect

from django.views.generic import TemplateView
from django.views.generic.edit import DeleteView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Server, ServerGroup, PackageUpdate
from django.contrib.auth.models import User


@method_decorator(login_required, name='dispatch')
class ServersControlPanelView(TemplateView):
	template_name = "server/servers.html"

	def get_context_data(self, **kwargs):
		context = super(ServersControlPanelView, self).get_context_data(**kwargs)
		context['servers'] = Server.objects.filter(user=self.request.user)
		context['server_groups'] = ServerGroup.objects.filter(user=self.request.user)
		context['install_script'] = "wget -O - http://{}/install/?u={} | bash".format( \
							self.request.get_host(), self.request.user.profile.uuid)
		return context


@method_decorator(login_required, name='dispatch')
class ServerDetails(DetailView):
	model = Server

	def get_context_data(self, **kwargs):
		context = super(ServerDetails, self).get_context_data(**kwargs)
		context['available_groups'] = ServerGroup.objects.filter(user=self.request.user) \
														 .exclude(servers=self.object)
		return context

@method_decorator(login_required, name='dispatch')
class ServerEditView(UpdateView):

	model = Server
	fields = ['ip', 'hostname']
	template_name = "server/server_edit.html"


	def get_success_url(self):
		return "{}?alert=1&updated=1".format(reverse('server_details', \
														args=[self.object.pk,]),)

	def form_valid(self, form):
		form.save()
		return super(ServerEditView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class ServerGroupView(DetailView):
	model = ServerGroup


@method_decorator(login_required, name='dispatch')
class PackageUpdateListView(ListView):
	model = PackageUpdate


@method_decorator(login_required, name='dispatch')
class DeleteGroupView(DeleteView):
	model = ServerGroup
	success_url = reverse_lazy('servers')


@login_required
def add_group(request):
	if request.method == 'POST':
		ServerGroup.objects.get_or_create(user=request.user, name=request.POST['name'])
	return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def assign_server_group(request):
	if request.method == 'POST':
		group = get_object_or_404(ServerGroup, pk=request.POST['groupid'])
		server = get_object_or_404(Server, pk=request.POST['serverid'])
		group.servers.add(server)
		group.save()
	return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def remove_server_group(request):
	if request.method == 'POST':
		group = get_object_or_404(ServerGroup, pk=request.POST['groupid'])
		server = get_object_or_404(Server, pk=request.POST['serverid'])
		group.servers.remove(server)
		group.save()
	return HttpResponseRedirect(request.META['HTTP_REFERER'])


def install_server(request):

	# Get hostname for URL
	__VAR_HOSTNAME_FOR_URL = "http://{}/install/".format(request.get_host(),)

	if request.method == "POST":
		user = request.POST['u']
		ip = request.POST['i']
		host = request.POST['h']
		dist = request.POST['d']
		port = request.POST['s']
		print(request.POST.items())

		s = Server.objects.filter(user=user, install=True).first_or_none()
		if s:
			s.install = False

		os.system('fab -H 127.0.0.1')
		# Check SSH connection.


		s.save()
		return HttpResponse("OK")


	elif request.method == "GET":
		user = request.GET['u']
		key_path = join(settings.PROJECT_ROOT, 'keys', user)

		# Generate key and assign them to var
		os.system('ssh-keygen -t rsa -b 4096 -C up2secure -f {} -N ""'.format(key_path,))
		private_key = os.popen('cat {}'.format(key_path)).read()
		__VAR_SSH_KEY = os.popen('cat {}'.format(key_path+".pub")).read()
		__VAR_USER = request.GET['u']

		user = User.objects.get(profile__uuid=__VAR_USER)
		server = Server.objects.create(user=user, 
									   public_key=__VAR_SSH_KEY,
									   private_key=private_key)

		# Open file with server instalation script.
		with open(join(settings.PROJECT_ROOT, 'server_install.sh'), 'r') as f:

			try:
				# Add variables to install script.
				install_script = f.read()
				install_script = install_script.replace('__VAR_HOSTNAME_FOR_URL', \
														 __VAR_HOSTNAME_FOR_URL)

				install_script = install_script.replace('__VAR_USER', __VAR_USER)
				install_script = install_script.replace('__VAR_SSH_KEY', __VAR_SSH_KEY)

			except Exception, e:
				print(e)

		return HttpResponse(install_script)

