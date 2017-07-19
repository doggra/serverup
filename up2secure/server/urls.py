from django.conf.urls import url

from .views import add_group
from .views import ServersControlPanelView, ServerDetails, ServerGroupView, \
				   UpdatesListView, DeleteGroupView


urlpatterns = [
	url(r'^$', ServersControlPanelView.as_view(), name='servers'),
	url(r'^details/(?P<pk>\d+)/$', ServerDetails.as_view(), name='server_details'),
	url(r'^group/(?P<pk>\d+)/$', ServerGroupView.as_view(), name='server_group'),
	url(r'^updates/', UpdatesListView.as_view(), name='updates'),
	url(r'^group/add/$', add_group, name='add_group'),
	url(r'^group/delete/(?P<pk>\d+)/$', DeleteGroupView.as_view(), name='delete_group')
]
