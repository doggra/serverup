# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.auth.models import User
from userland.models import Customer, Reseller, Profile


class OwnProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class CustomerForm(forms.ModelForm):

    password = forms.CharField()
    email = forms.EmailField(label="Email address")
    reseller = forms.ModelChoiceField(\
                        required=False,
                        label="Reseller",
                        queryset=User.objects\
                                     .filter(reseller__isnull=False,
                                             is_active=True))

    limit = forms.IntegerField(initial=1, label="Servers limit", min_value=1)

    def save(self):
        m = super(CustomerForm, self).save(commit=False)
        m.set_password(self.cleaned_data['password'])
        m.save()
        Customer.objects.create(user=m, 
                                servers_limit=self.cleaned_data['limit'],
                                reseller=self.cleaned_data['reseller'])
        Profile.objects.create(user=m, account_type=0)
        return m

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 
                  'first_name', 'last_name', 'reseller', 'limit']


class ResellerForm(forms.ModelForm):

    email = forms.EmailField(label="Email address")
    password = forms.CharField(widget=forms.PasswordInput())
    limit = forms.IntegerField(initial=0, label="Customers limit")

    def save(self):
        m = super(CustomerForm, self).save(commit=False)
        m.set_password(self.cleaned_data['password'])
        m.save()
        Reseller.objects.create(user=m, 
                                customers_limit=self.cleaned_data['limit'])
        Profile.objects.create(user=m, account_type=1)
        return m

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 
                  'first_name', 'last_name', 'limit']
