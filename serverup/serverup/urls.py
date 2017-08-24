from django.conf.urls import include, url
from django.contrib import admin

from userland.views import Dashboard, OwnProfile, OwnProfileEdit, History, LoginView, \
				   LogoutView, ChangePasswordView, CustomerListView, ResellerListView, \
				   Accounting, CustomerEditView, accounting_paypal, paypal_return, \
				   paypal_cancel, CustomerCreateView, ResellerCreateView, \
				   CustomerDeleteView, ResellerDeleteView, ResellerEditView

from django.contrib.auth import views as auth_views

from server.views import PackageUpdateListView, install_server


urlpatterns = [

	# User Land
	url(r'^$', Dashboard.as_view(), name='dashboard'),

	url(r'^login/$', LoginView.as_view(), name='login'),
	url(r'^logout/$', LogoutView.as_view(), name='logout'),
	# url(r'^profile/password-reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),


	url(r'^profile/$', OwnProfile.as_view(), name='own_profile'),
	url(r'^profile/edit/$', OwnProfileEdit.as_view(), name='own_profile_edit'),
	url(r'^profile/password/change/$', ChangePasswordView.as_view(), name='password_change'),
		
	url(r'^updates/', PackageUpdateListView.as_view(), name='updates'),
	url(r'^history/$', History.as_view(), name='history'),

	# App
	url(r'^server/', include('server.urls')),
	url(r'^accounting/$', Accounting.as_view(), name='accounting'),
	url(r'^accounting/paypal/$', accounting_paypal, name='accounting_paypal'),

	url(r'^paypal/', include('paypal.standard.ipn.urls')),
	url(r'^paypal/return/$', paypal_return, name='paypal-return-view'),
	url(r'^paypal/cancel/$', paypal_cancel, name='paypal-cancel-view'),

	url(r'^customer/list/$', CustomerListView.as_view(), name='customer_list'),
	url(r'^customer/create/$', CustomerCreateView.as_view(), name='customer_create'),
	url(r'^customer/delete/(?P<uuid>[\w-]+)/$', CustomerDeleteView.as_view(), name='customer_delete'),
	url(r'^customer/edit/(?P<uuid>[\w-]+)/$', CustomerEditView.as_view(), name='customer_edit'),

	url(r'^reseller/create/$', ResellerCreateView.as_view(), name='reseller_create'),
	url(r'^reseller/list/$', ResellerListView.as_view(), name='reseller_list'),
	url(r'^reseller/delete/(?P<uuid>[\w-]+)/$', ResellerDeleteView.as_view(), name='reseller_delete'),
	url(r'^reseller/edit/(?P<uuid>[\w-]+)/$', ResellerEditView.as_view(), name='reseller_edit'),

	# Install server
	url(r'^install/$', install_server, name='install_server'),

	# Admin Zone
	url(r'^sudosu/', include(admin.site.urls)),
]
