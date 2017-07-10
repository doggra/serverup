from django.conf.urls import include, url
from django.contrib import admin

from userland.views import Home, Servers, Updates, Accounting

urlpatterns = [

	# User Land
	url(r'^$', Home.as_view(), name='home'),
	url(r'^servers/$', Servers.as_view(), name='servers'),
	url(r'^updates/$', Updates.as_view(), name='updates'),
	url(r'^accounting/$', Accounting.as_view(), name='accounting'),

	# Admin Zone
    url(r'^sudosu/', include(admin.site.urls)),
]
