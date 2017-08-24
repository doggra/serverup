# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views

from django.views.generic import View, TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, CreateView
from django.views.generic.edit import UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

from .models import Profile, Customer, Reseller
from .forms import CustomerForm
from .forms import ResellerForm
from .forms import OwnProfileEditForm

from server.models import Server, PackageUpdate

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.forms import PayPalPaymentsForm


@method_decorator(login_required, name='dispatch')
class Dashboard(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        servers = Server.objects.filter(user=self.request.user).exclude(status=3)
        context['servers_count'] = servers.count()
        context['updates_count'] = PackageUpdate.objects.filter(\
                                                    user=self.request.user,
                                                    ignore=False).count()

        if self.request.user.profile.account_type == 1:
            context['customers_count'] = Customer.objects.filter(\
                                        reseller=self.request.user,
                                        user_is_active=True).count()
        elif self.request.user.profile.account_type == 2:
            context['customers_count'] = Customer.objects.filter(user__is_active=True).count()
            context['resellers_count'] = Reseller.objects.filter(user__is_active=True).count()

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
class CustomerCreateView(FormView):
    form_class = CustomerForm
    template_name = 'userland/customer_create.html'
    success_url = reverse_lazy('customer_list')

    def form_valid(self, form):
        form.save()
        return super(CustomerCreateView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class CustomerDeleteView(DeleteView):
    model = User
    success_url = reverse_lazy('customer_list')

    def get_object(self):
        acc_type = self.request.user.profile.account_type
        profile = get_object_or_404(Profile, uuid=self.kwargs['uuid'])
        if acc_type == 0:
            raise PermissionDenied
        if acc_type == 1:
            if profile.user.customer.reseller != self.request.user:
                raise PermissionDenied
        return profile.user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return HttpResponseRedirect(reverse_lazy('customer_list'))


@method_decorator(login_required, name='dispatch')
class CustomerListView(ListView):
    model = Customer

    def get_context_data(self, **kwargs):
        context = super(CustomerListView, self).get_context_data(**kwargs)
        context['resellers'] = Reseller.objects.filter(user__is_active=True)
        return context

    def get_queryset(self):
        acc_type = self.request.user.profile.account_type
        if acc_type == 0:
            raise PermissionDenied
        elif acc_type == 1:
            return Customer.objects.filter(reseller=self.request.user,
                                           user__is_active=True)
        elif acc_type == 2:
            return Customer.objects.filter(user__is_active=True)


@method_decorator(login_required, name='dispatch')
class CustomerEditView(FormView):
    form_class = CustomerForm
    template_name = 'userland/customer_edit.html'
    success_url = reverse_lazy('customer_list')

    def post(self, request, uuid):
        user = self.get_object()
        form = CustomerForm(request.POST, instance=user)
        form.fields['password'].required = False

        if form.is_valid():
            data = form.cleaned_data
            user.username = data['username']
            user.email = data['email']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.email = data['email']
            user.save()
            user.customer.reseller = data['reseller']
            user.customer.servers_limit = data['limit']
            user.customer.save()

        return HttpResponseRedirect(reverse('customer_list'))

    def get_object(self):
        profile = get_object_or_404(Profile, uuid=self.kwargs['uuid'])
        return profile.user

    def get_form(self):
        user = self.get_object()
        form = CustomerForm(instance=user,
                            initial={'limit': user.customer.servers_limit,
                                     'reseller': user.customer.reseller})
        del form.fields['password']
        return form


@method_decorator(login_required, name='dispatch')
class ResellerCreateView(FormView):
    form_class = ResellerForm
    template_name = 'userland/reseller_create.html'
    success_url = reverse_lazy('reseller_list')

    def form_valid(self, form):
        form.save()
        return super(ResellerCreateView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class ResellerListView(ListView):
    model = Reseller

    def get_context_data(self, **kwargs):
        context = super(ResellerListView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        acc_type = self.request.user.profile.account_type
        if acc_type == 0 or acc_type == 1:
            raise PermissionDenied
        elif acc_type == 2:
            return Reseller.objects.filter(user__is_active=True)


@method_decorator(login_required, name='dispatch')
class ResellerDeleteView(DeleteView):
    model = User
    success_url = reverse_lazy('reseller_list')

    def get_object(self):
        acc_type = self.request.user.profile.account_type
        profile = get_object_or_404(Profile, uuid=self.kwargs['uuid'])
        if acc_type in [0, 1]:
            raise PermissionDenied
        return profile.user

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return HttpResponseRedirect(reverse_lazy('reseller_list'))


@method_decorator(login_required, name='dispatch')
class ResellerEditView(FormView):
    form_class = ResellerForm
    template_name = 'userland/reseller_edit.html'
    success_url = reverse_lazy('reseller_list')

    def post(self, request, uuid):
        user = self.get_object()
        form = ResellerForm(request.POST, instance=user)
        form.fields['password'].required = False

        if form.is_valid():
            data = form.cleaned_data
            user.username = data['username']
            user.email = data['email']
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.email = data['email']
            user.save()
            user.reseller.customers_limit = data['limit']
            user.reseller.save()

        return HttpResponseRedirect(reverse('reseller_list'))

    def get_object(self):
        profile = get_object_or_404(Profile, uuid=self.kwargs['uuid'])
        return profile.user

    def get_form(self):
        user = self.get_object()
        form = ResellerForm(instance=user,
                            initial={'limit': user.reseller.customers_limit})
        del form.fields['password']
        return form


@method_decorator(login_required, name='dispatch')
class Accounting(TemplateView):
    template_name = "userland/accounting.html"


# @method_decorator(login_required, name='dispatch')
# class AccountingPayPal(TemplateView):
#     template_name = "userland/accounting_paypal.html"


@login_required
def accounting_paypal(request):

    # What you want the button to do.
    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": 100.00,
        "item_name": "name of the item",
        "invoice": "unique-invoice-id",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return_url": request.build_absolute_uri(reverse('paypal-return-view')),
        "cancel_return": request.build_absolute_uri(reverse('paypal-cancel-view')),
    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
    return render(request, "userland/accounting_paypal.html", context)


def show_me_the_money(sender, **kwargs):

    ipn_obj = sender
    print(ipn_obj)

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        # WARNING !
        # Check that the receiver email is the same we previously
        # set on the `business` field. (The user could tamper with
        # that fields on the payment form before it goes to PayPal)
        if ipn_obj.receiver_email != "receiver_email@example.com":
            # Not a valid payment
            return

        # ALSO: for the same reason, you need to check the amount
        # received, `custom` etc. are all what you expect or what
        # is allowed.

        # Undertake some action depending upon `ipn_obj`.
        # if ipn_obj.custom == "premium_plan":
        #     price = ...
        # else:
        #     price = ...
        print('complete!')
    #     if ipn_obj.mc_gross == price and ipn.mc_currency == 'USD':
    #         ...
    # else:
    #     #...

@csrf_exempt
@login_required
def paypal_return(request):
    return render(request, 'userland/paypal-return.html')


@login_required
def paypal_cancel(request):
    return render(request, 'userland/paypal-cancel.html')


valid_ipn_received.connect(show_me_the_money)