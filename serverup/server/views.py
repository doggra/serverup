# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
import os
import paramiko
import StringIO
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
from django.views.decorators.csrf import csrf_exempt


@method_decorator(login_required, name='dispatch')
class Servers(TemplateView):
	template_name = "server/servers.html"

	def get_context_data(self, **kwargs):
		context = super(Servers, self).get_context_data(**kwargs)

		# Display all servers if user is superuser
		if self.request.user.is_staff:
			context['servers'] = Server.objects.exclude(status=3)
		else:
			context['servers'] = Server.objects.filter(user=self.request.user).exclude(status=3)
		context['server_limit'] = self.request.user.profile.server_limit
		context['updates'] = PackageUpdate.objects.filter(status=1)
		context['server_groups'] = ServerGroup.objects.filter(user=self.request.user)
		context['install_script'] = "wget -O - http://{}/install/?u={} | bash".format( \
							self.request.get_host(), self.request.user.profile.uuid)
		return context


@method_decorator(login_required, name='dispatch')
class ServerDetails(DetailView):
	model = Server

	def get_object(self):
		return get_object_or_404(Server, uuid=self.kwargs['uuid'])

	def get_context_data(self, **kwargs):
		context = super(ServerDetails, self).get_context_data(**kwargs)
		context['updates'] = PackageUpdate.objects.filter(server=self.object,status__in=[0, 2])
		context['available_groups'] = ServerGroup.objects.filter(user=self.request.user) \
														 .exclude(servers=self.object)
		return context

@method_decorator(login_required, name='dispatch')
class ServerEditView(UpdateView):

	model = Server
	fields = ['ip', 'hostname']
	template_name = "server/server_edit.html"

	def get_object(self):
		return get_object_or_404(Server, uuid=self.kwargs['uuid'])

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
class ServerGroupDeleteView(DeleteView):
	model = ServerGroup
	success_url = reverse_lazy('servers')


@method_decorator(login_required, name='dispatch')
class ServerDeleteView(DeleteView):
	model = Server
	success_url = reverse_lazy('servers')

	def get_object(self):
		return get_object_or_404(Server, uuid=self.kwargs['uuid'])


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


@csrf_exempt
def install_server(request):

	# Get apps hostname.
	__VAR_HOSTNAME_FOR_URL = "http://{}/install/".format(request.get_host(),)

	# Response from installation script.
	if request.method == "POST":
		user = request.POST['u']
		ip = request.POST['i']
		host = request.POST['h']
		dist = request.POST['d']
		port = request.POST['p']
		s_uuid = request.POST['s']

		# Get Server or 404
		s = get_object_or_404(Server, user__profile__uuid=user, uuid=s_uuid)
		s.hostname = host
		s.ip = ip

		try:
			s.os = int(dist)
		except TypeError:
			s.os = -1

		try:
			s.ssh_port = int(port)
		except TypeError:
			pass

		# Installed.
		s.save()
		s.status = 0

		# Check SSH connection.
		response = s.check_updates()
		if "FAIL" not in response:
			return HttpResponse("OK")
		else:
			return HttpResponse(response)

	elif request.method == "GET":
		user = request.GET['u']
		private_key_path = join(settings.PROJECT_ROOT, 'keys', user)

		try:
			# Generate ssh key and assign it to var
			os.system('ssh-keygen -t rsa -b 4096 -C serverup -f {} -N ""'.format(private_key_path,))
			private_key = os.popen('cat {}'.format(private_key_path)).read()
			__VAR_SSH_KEY = os.popen('cat {}'.format(private_key_path+".pub")).read()
			__VAR_USER = str(request.GET.get('u', ''))
			user = User.objects.filter(profile__uuid=__VAR_USER)

			if user:
				server = Server.objects.create(user=user[0],
											   public_key=__VAR_SSH_KEY,
											   private_key=private_key)

				__VAR_SERVER_UUID = str(server.uuid)

				# Open file with server instalation script.
				with open(join(settings.PROJECT_ROOT, 'server_install.sh'), 'r') as f:

					# Substitute variables in installation script.
					try:
						install_script = f.read()
						install_script = install_script.replace('__VAR_HOSTNAME_FOR_URL', \
																 __VAR_HOSTNAME_FOR_URL)

						install_script = install_script.replace('__VAR_SERVER_UUID', \
																 __VAR_SERVER_UUID)

						install_script = install_script.replace('__VAR_USER', __VAR_USER)
						install_script = install_script.replace('__VAR_SSH_KEY', __VAR_SSH_KEY)


					except Exception, e:
						print(e)

				return HttpResponse(install_script)

		except Exception, e:
			print(e)

		finally:
			os.system('rm %s' % private_key_path)