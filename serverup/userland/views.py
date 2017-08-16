# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views

from django.views.generic import View, TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .models import Customer, Reseller
from .forms import OwnProfileEditForm
from server.models import Server, PackageUpdate

from django.contrib.auth.decorators import user_passes_test


@method_decorator(login_required, name='dispatch')
class Dashboard(TemplateView):
	template_name = "dashboard.html"

	def get_context_data(self, **kwargs):
		context = super(Dashboard, self).get_context_data(**kwargs)
		if self.request.user.profile.account_type == 0:
			servers = Server.objects.filter(user=self.request.user).exclude(status=3)
		elif self.request.user.profile.account_type == 1:
			servers = Server.objects.filter(user__customer__reseller=self.request.user)
		elif self.request.user.profile.account_type == 2:
			servers = Server.objects.all()

		# Exclude servers with INSTALL status.
		servers = servers.exclude(status=3)

		context['servers_count'] = servers.count()
		context['updates_count'] = PackageUpdate.objects.filter(user=self.request.user,
																ignore=False).count()
		return context


@method_decorator(login_required, name='dispatch')
class History(TemplateView):
	template_name = "userland/history.html"


@method_decorator(login_required, name='dispatch')
class OwnProfile(TemplateView):
	template_name = "userland/own_profile_show.html"


@method_decorator(login_required, name='dispatch')
class OwnProfileEdit(UpdateView):

	model = User
	fields = ['first_name', 'last_name', 'email']
	template_name = "userland/own_profile_edit.html"

 	def get_object(self):
 		return self.request.user

	def get_success_url(self):
		return "{}?alert=1&updated=1".format(reverse('own_profile'),)

	def form_valid(self, form):
		form.save()
		return super(OwnProfileEdit, self).form_valid(form)


class LoginView(TemplateView):
	template_name = "login.html"

	def post(self, request):
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)

		if user is not None:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/')

		if user is None or not user.is_active:
			return HttpResponseRedirect("{}?invalid=1".format(reverse('login'),))


@method_decorator(login_required, name='dispatch')
class LogoutView(View):
	def get(self, request):
		logout(request)
		return HttpResponseRedirect(settings.LOGIN_URL)


@method_decorator(login_required, name='dispatch')
class ChangePasswordView(auth_views.PasswordChangeView):
	template_name = 'userland/own_pass_change_form.html'

	def get_success_url(self):
		return "{}?alert=1&password_changed=1".format(reverse('own_profile'),)


@method_decorator(login_required, name='dispatch')
class CustomerListView(ListView):
	model = Customer


@method_decorator(login_required, name='dispatch')
class ResellerListView(ListView):
    model = Reseller


@method_decorator(login_required, name='dispatch')
class Accounting(TemplateView):
	template_name = "userland/accounting.html"
