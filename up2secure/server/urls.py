from django.conf.urls import url

from .views import ServerListView, ServerGroup

urlpatterns = [
	url(r'^$', ServerListView.as_view(), name='server_list'),
	url(r'^(?P<user_id>\d+)/(?P<group_id>\d+)/$', ServerGroup.as_view(), name='server_group'),
]