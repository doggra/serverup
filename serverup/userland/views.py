# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.urls import reverse
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views

from django.views.generic import View, TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

from .models import Profile, Customer, Reseller
from .forms import OwnProfileEditForm, UserEditForm
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
                                        reseller=self.request.user).count()
        elif self.request.user.profile.account_type == 2:
            context['customers_count'] = Customer.objects.count()
            context['resellers_count'] = Reseller.objects.count()

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

    def get_context_data(self, **kwargs):
        context = super(CustomerListView, self).get_context_data(**kwargs)
        context['user_form'] = UserEditForm()
        context['resellers'] = Reseller.objects.all()
        return context

    def get_queryset(self):
        acc_type = self.request.user.profile.account_type
        if acc_type == 0:
            raise PermissionDenied
        elif acc_type == 1:
            return Customer.objects.filter(reseller=self.request.user)
        elif acc_type == 2:
            return Customer.objects.all()


@method_decorator(login_required, name='dispatch')
class ResellerListView(ListView):
    model = Reseller

    def get_context_data(self, **kwargs):
        context = super(ResellerListView, self).get_context_data(**kwargs)
        context['user_form'] = UserEditForm()
        return context

    def get_queryset(self):
        acc_type = self.request.user.profile.account_type
        if acc_type == 0 or acc_type == 1:
            raise PermissionDenied
        elif acc_type == 2:
            return Reseller.objects.all()


@method_decorator(login_required, name='dispatch')
class ResellerEditView(TemplateView):
    template_name = "userland/reseller_edit.html"

    def get_context_data(self, **kwargs):
        context = super(ResellerEditView, self).get_context_data(**kwargs)
        profile = get_object_or_404(Profile, uuid=kwargs['uuid'])
        context['reseller'] = profile.user.reseller
        context['form'] = UserEditForm(instance=profile.user)
        return context

    def post(self, request, uuid):
        profile = get_object_or_404(Profile, uuid=uuid)
        form = UserEditForm(instance=profile.user, data=request.POST)
        if form.is_valid:
            user = form.save()

            # Set new password if changed.
            new_pass = request.POST.get('new_password', '')
            if new_pass != '':
                user.set_password(new_pass)
                user.save()

            reseller = Reseller.objects.get(user=user)
            new_limit = request.POST.get('customers_limit', None)

            if new_limit:
                reseller.customers_limit = new_limit
                reseller.save()

            reseller.save()

        return HttpResponseRedirect(reverse('reseller_list'))


@method_decorator(login_required, name='dispatch')
class CustomerEditView(TemplateView):
    template_name = "userland/customer_edit.html"

    def get_context_data(self, **kwargs):
        context = super(CustomerEditView, self).get_context_data(**kwargs)
        profile = get_object_or_404(Profile, uuid=kwargs['uuid'])
        context['customer'] = profile.user.customer
        context['form'] = UserEditForm(instance=profile.user)
        context['resellers'] = Reseller.objects.all()

        # Let in only administrator or reseller assigned to that customer.
        acc_type = self.request.user.profile.account_type
        if acc_type == 0:
            raise PermissionDenied
        elif acc_type == 1:
            if self.request.user != context['customer'].reseller:
                raise PermissionDenied
        return context

    def post(self, request, uuid):
        profile = get_object_or_404(Profile, uuid=uuid)
        form = UserEditForm(instance=profile.user, data=request.POST)
        if form.is_valid:
            user = form.save()

            # Set new password if changed.
            new_pass = request.POST.get('new_password', '')
            if new_pass != '':
                user.set_password(new_pass)
                user.save()

            customer = Customer.objects.get(user=user)
            new_limit = request.POST.get('servers_limit', None)

            if new_limit:
                customer.servers_limit = new_limit
                customer.save()

            reseller_pk = request.POST.get('reseller', None)

            if reseller_pk:
                reseller = User.objects.get(pk=reseller_pk)
                customer.reseller = reseller

            customer.save()

        return HttpResponseRedirect(reverse('customer_list'))


@login_required
def create_customer(request):
    if request.method == 'POST':
        user_form = UserEditForm(data=request.POST)

        if user_form.is_valid():
            user = User.objects.create_user(user_form.cleaned_data['username'], 
                                            user_form.cleaned_data['email'],
                                            request.POST.get('password', ''),
                                            last_name=user_form.cleaned_data['last_name'])

            # Check if servers limit is more than 0 (Customers must have servers limit).
            # Create customer and profile objects.
            lmt = request.POST.get('servers_limit', 1)
            if request.user.profile.account_type == 2:
                reseller = Reseller.objects.get(user=request.POST.get('reseller', None)).user
            else:
                reseller = request.user

            profile = Profile.objects.create(user=user, account_type=0)
            Customer.objects.create(user=user, 
                                    servers_limit=max(1,lmt),
                                    reseller=reseller)

        else:
            print(user_form.errors)

    return HttpResponseRedirect(reverse('customer_list'))


@login_required
def create_reseller(request):
    if request.method == 'POST':
        user_form = UserEditForm(data=request.POST)

        if user_form.is_valid():
            user = User.objects.create_user(user_form.cleaned_data['username'], 
                                            user_form.cleaned_data['email'],
                                            request.POST.get('password', ''),
                                            last_name=user_form.cleaned_data['last_name'])

            # Create reseller and profile objects.
            lmt = request.POST.get('customers_limit', 1)
            profile = Profile.objects.create(user=user, account_type=1)
            Reseller.objects.create(user=user, 
                                    customers_limit=max(1,lmt))

        else:
            print(user_form.errors)

    return HttpResponseRedirect(reverse('reseller_list'))


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
        "business": "receiver_email@example.com",
        "amount": "10000000.00",
        "item_name": "name of the item",
        "invoice": "unique-invoice-id",
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return_url": request.build_absolute_uri(reverse('paypal-return-view')),
        "cancel_return": request.build_absolute_uri(reverse('paypal-cancel-view')),
        "custom": "premium_plan",  # Custom command to correlate to some function later (optional)
    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
    return render(request, "userland/accounting_paypal.html", context)



@login_required
def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
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
        print(ipn_obj)
    #     if ipn_obj.mc_gross == price and ipn.mc_currency == 'USD':
    #         ...
    # else:
    #     #...

@csrf_exempt
@login_required
def paypal_return(request):
    return render('userland/paypal-return.html')


@login_required
def paypal_cancel(request):
    return render('userland/paypal-cancel.html')


valid_ipn_received.connect(show_me_the_money)