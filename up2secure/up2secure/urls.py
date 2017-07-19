from django.conf.urls import include, url
from django.contrib import admin

from userland.views import Dashboard, OwnProfile, OwnProfileEdit, History, LoginView, \
				   LogoutView, ChangePasswordView, CustomerListView, ResellerListView, \
				   Accounting

from django.contrib.auth import views as auth_views

from server.views import install_server

urlpatterns = [

	# User Land
	url(r'^$', Dashboard.as_view(), name='dashboard'),

	url(r'^login/$', LoginView.as_view(), name='login'),
	url(r'^logout/$', LogoutView.as_view(), name='logout'),
	# url(r'^profile/password-reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),


	url(r'^profile/$', OwnProfile.as_view(), name='own_profile'),
	url(r'^profile/edit/$', OwnProfileEdit.as_view(), name='own_profile_edit'),
	url(r'^profile/password/change/$', ChangePasswordView.as_view(), name='password_change'),

		

	url(r'^history/$', History.as_view(), name='history'),

	# App
	url(r'^server/', include('server.urls')),
	url(r'^accounting/$', Accounting.as_view(), name='accounting'),
	url(r'^customer/list/$', CustomerListView.as_view(), name='customer_list'),
	url(r'^reseller/list/$', ResellerListView.as_view(), name='reseller_list'),

	# Install server
	url(r'^install/$', install_server, name='install_server'),

	# Admin Zone
	url(r'^sudosu/', include(admin.site.urls)),
]
