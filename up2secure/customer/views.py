# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


from .models import Customer


@method_decorator(login_required, name='dispatch')
class CustomerListView(ListView):
	model = Customer


@method_decorator(login_required, name='dispatch')
class Accounting(TemplateView):
	template_name = "customer/accounting.html"
