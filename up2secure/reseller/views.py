# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from .models import Reseller


@method_decorator(login_required, name='dispatch')
class ResellerListView(ListView):
    model = Reseller
