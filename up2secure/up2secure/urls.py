from django.conf.urls import include, url
from django.contrib import admin

from userland.views import Home

urlpatterns = [

	# User Land
	url(r'^$', Home.as_view(), name='home'),

	# Admin Zone
    url(r'^sudosu/', include(admin.site.urls)),
]
