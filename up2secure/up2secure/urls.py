from django.conf.urls import include, url
from django.contrib import admin

from userland.views import Dashboard, History, LoginView, LogoutView

urlpatterns = [

	# User Land
	url(r'^$', Dashboard.as_view(), name='dashboard'),
	url(r'^history/$', History.as_view(), name='history'),
	url(r'^login/$', LoginView.as_view(), name='login'),
	url(r'^logout/$', LogoutView.as_view(), name='logout'),

	# App
	url(r'^server/', include('server.urls')),
	url(r'^reseller/', include('reseller.urls')),
	url(r'^customer/', include('customer.urls')),

	# Admin Zone
    url(r'^sudosu/', include(admin.site.urls)),
]
