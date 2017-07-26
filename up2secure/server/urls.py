from django.conf.urls import url

from .views import add_group, assign_server_group, remove_server_group
from .views import Servers, ServerDetails, ServerGroupView, \
				   PackageUpdateListView, ServerGroupDeleteView, ServerEditView, \
				   ServerDeleteView


urlpatterns = [
	url(r'^$', Servers.as_view(), name='servers'),
	url(r'^details/(?P<uuid>[\w-]+)/$', ServerDetails.as_view(), name='server_details'),
	url(r'^edit/(?P<uuid>[\w-]+)/$', ServerEditView.as_view(), name='server_edit'),
	url(r'^delete/(?P<uuid>[\w-]+)/$', ServerDeleteView.as_view(), name='server_delete'),
	url(r'^group/(?P<pk>\d+)/$', ServerGroupView.as_view(), name='server_group'),
	url(r'^updates/', PackageUpdateListView.as_view(), name='updates'),
	url(r'^group/add/$', add_group, name='add_group'),
	url(r'^group/assign/$', assign_server_group, name='assign_server_group'),
	url(r'^group/remove/$', remove_server_group, name='remove_server_group'),
	url(r'^group/delete/(?P<pk>\d+)/$', ServerGroupDeleteView.as_view(), name='delete_group')
]
