from django.conf.urls import include, url
from django.contrib import admin

from userland.views import Dashboard, History, Accounting


urlpatterns = [

	# User Land
	url(r'^$', Dashboard.as_view(), name='dashboard'),
	url(r'^history/$', History.as_view(), name='history'),
	url(r'^accounting/$', Accounting.as_view(), name='accounting'),

	url(r'^server/', include('server.urls')),
	url(r'^reseller/', include('reseller.urls')),
	url(r'^customer/', include('customer.urls')),

	# Admin Zone
    url(r'^sudosu/', include(admin.site.urls)),
]
