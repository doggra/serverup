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

from userland.models import Customer
from .models import Server, ServerGroup, PackageUpdate
from .tasks import task_check_updates, task_update_server, task_update_package
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from history.models import Event

def test_server_owner(request, server):
	if request.user.id != server.user.id:
		raise PermissionDenied
		return None
	return server


@method_decorator(login_required, name='dispatch')
class Servers(TemplateView):
	template_name = "server/servers.html"

	def get_context_data(self, **kwargs):
		context = super(Servers, self).get_context_data(**kwargs)

		context['servers'] = Server.objects.filter(user=self.request.user).exclude(status=3)
		context['updates'] = PackageUpdate.objects.all()
		context['server_groups'] = ServerGroup.objects.filter(user=self.request.user)
		context['install_script'] = "wget -O - http://{}/install/?u={} | bash".format( \
							self.request.get_host(), self.request.user.profile.uuid)

		# Get servers limit - (only customer) if not exists - show 0
		try:
			context['servers_limit'] = self.request.user.customer.servers_limit
		except Customer.DoesNotExist:
			context['servers_limit'] = 0

		return context


@method_decorator(login_required, name='dispatch')
class ServerDetails(DetailView):
	model = Server

	def get_object(self):
		server = get_object_or_404(Server, uuid=self.kwargs['uuid'])
		return test_server_owner(self.request, server)


	def get_context_data(self, **kwargs):
		context = super(ServerDetails, self).get_context_data(**kwargs)
		context['updates'] = PackageUpdate.objects.filter(server=self.object)
		context['available_groups'] = ServerGroup.objects.filter(user=self.request.user) \
														 .exclude(servers=self.object)
		context['events'] = Event.objects.filter(server=self.object)

		return context


@method_decorator(login_required, name='dispatch')
class ServerEditView(UpdateView):

	model = Server
	fields = ['ip', 'hostname', 'ssh_port', 'public_key', 'private_key']
	template_name = "server/server_edit.html"

	def get_object(self):
		server = get_object_or_404(Server, uuid=self.kwargs['uuid'])
		return test_server_owner(self.request, server)

	def get_success_url(self):
		return "{}?alert=1&updated=1".format(reverse('server_details', \
														args=[self.object.pk,]),)

	def form_valid(self, form):
		form.save()
		return super(ServerEditView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class ServerDeleteView(DeleteView):
	model = Server
	success_url = reverse_lazy('servers')

	def get_object(self):
		server = get_object_or_404(Server, uuid=self.kwargs['uuid'])
		return test_server_owner(self.request, server)


@method_decorator(login_required, name='dispatch')
class ServerGroupView(DetailView):
	model = ServerGroup


@method_decorator(login_required, name='dispatch')
class ServerGroupDeleteView(DeleteView):
	model = ServerGroup
	success_url = reverse_lazy('servers')


@method_decorator(login_required, name='dispatch')
class PackageUpdateListView(ListView):
	model = PackageUpdate

	def get_queryset(self):
		queryset = PackageUpdate.objects.filter(user=self.request.user)
		return queryset


### Server groups API

@login_required
def add_group(request):
	if request.method == 'POST':
		ServerGroup.objects.get_or_create(user=request.user,
										  name=request.POST['name'])
	return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def assign_server_group(request):
	if request.method == 'POST':
		group = get_object_or_404(ServerGroup, pk=request.POST['groupid'])
		server = get_object_or_404(Server, pk=request.POST['serverid'])

		test_server_owner(self.request, server)

		group.servers.add(server)
		group.save()
	return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def remove_server_group(request):
	if request.method == 'POST':
		group = get_object_or_404(ServerGroup, pk=request.POST['groupid'])
		server = get_object_or_404(Server, pk=request.POST['serverid'])

		test_server_owner(self.request, server)

		group.servers.remove(server)
		group.save()
	return HttpResponseRedirect(request.META['HTTP_REFERER'])


### Update API

@login_required
def server_check_updates(request, uuid):
	s = get_object_or_404(Server, uuid=uuid)

	test_server_owner(request, s)

	s.status = 2
	s.save()
	task_check_updates.apply_async((uuid,))
	return HttpResponseRedirect(reverse_lazy('server_details', args=[uuid,]))


@login_required
def server_update_all(request, uuid):
	s = get_object_or_404(Server, uuid=uuid)

	test_server_owner(request, s)

	s.status = 2
	s.save()
	task_update_server.apply_async((uuid,))
	return HttpResponseRedirect(reverse_lazy('server_details', args=[uuid,]))


@login_required
def server_change_auto_updates(request, uuid):
	s = get_object_or_404(Server, uuid=uuid)

	test_server_owner(request, s)

	s.toggle_auto_updates()
	return HttpResponse(s.auto_updates)


@login_required
def server_change_update_interval(request, uuid):
	interval = request.POST.get('interval', 24)
	s = get_object_or_404(Server, uuid=uuid)

	test_server_owner(request, s)

	s.update_interval = interval
	s.save()
	return HttpResponseRedirect(reverse_lazy('server_details', args=[uuid,]))


@login_required
def package_change_ignore(request, package_id):
	package = get_object_or_404(PackageUpdate, pk=package_id)

	test_server_owner(request, package.server)

	package.ignore = True if package.ignore == False else False
	package.save()
	return HttpResponse("OK")


@login_required
def package_manual_update(request, uuid, package_name):
	server = get_object_or_404(Server, uuid=uuid)

	test_server_owner(request, server)

	task_update_package.apply_async((uuid, package_name))
	return HttpResponseRedirect(reverse_lazy('server_details', args=[uuid,]))


### Server API

@login_required
def check_server_status(request, uuid):
	server = get_object_or_404(Server, uuid=uuid)
	test_server_owner(request, server)
	if request.GET.get('dspl', '') == '1':
		return HttpResponse(server.show_status)
	return HttpResponse(server.status)


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

		# Check SSH connection.
		response = s.send_command('id')
		if 'uid=0' not in response:
			return HttpResponse(response)

		# Installed.
		s.status = 0
		s.save()

		# # Check for updates
		# s.check_updates()

		return HttpResponse("OK")

	elif request.method == "GET":
		user = request.GET['u']
		private_key_path = join(settings.PROJECT_ROOT, 'keys', user)

		try:

			# Generate ssh key pair.
			os.system(('ssh-keygen -t rsa -b 4096 '
					   '-C serverup -f {} -N ""').format(private_key_path,))
			private_key = os.popen('cat {}'.format(private_key_path)).read()
			__VAR_SSH_KEY = os.popen('cat {}'.format(private_key_path+".pub"))\
																		.read()

			# Get user by uuid.
			__VAR_USER = str(request.GET.get('u', ''))
			user = User.objects.filter(profile__uuid=__VAR_USER)
			if user:
				server = Server.objects.create(user=user[0],
											   public_key=__VAR_SSH_KEY,
											   private_key=private_key)

				Event.objects.create(server=server, event_type=1)

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