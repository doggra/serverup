from django.conf.urls import url

from .views import add_group, assign_server_group, remove_server_group, \
				   server_check_updates, server_update_all, \
				   package_change_ignore, package_manual_update, \
				   server_change_auto_updates, server_change_update_interval, \
				   check_server_status

from .views import Servers, ServerDetails, ServerGroupView, \
				   PackageUpdateListView, ServerGroupDeleteView, \
				   ServerEditView, ServerDeleteView

urlpatterns = [
	url(r'^$', Servers.as_view(), name='servers'),

	url(r'^details/(?P<uuid>[\w-]+)/$', ServerDetails.as_view(), name='server_details'),
	url(r'^edit/(?P<uuid>[\w-]+)/$', ServerEditView.as_view(), name='server_edit'),
	url(r'^delete/(?P<uuid>[\w-]+)/$', ServerDeleteView.as_view(), name='server_delete'),
	url(r'^details/(?P<uuid>[\w-]+)/$', ServerDetails.as_view(), name='server_details'),
	url(r'^group/(?P<pk>\d+)/$', ServerGroupView.as_view(), name='server_group'),

	url(r'^group/add/$', add_group, name='add_group'),
	url(r'^group/assign/$', assign_server_group, name='assign_server_group'),
	url(r'^group/remove/$', remove_server_group, name='remove_server_group'),
	url(r'^group/delete/(?P<pk>\d+)/$', ServerGroupDeleteView.as_view(), name='delete_group'),

	url(r'^check/(?P<uuid>[\w-]+)/$', server_check_updates, name='server_check_updates'),
	url(r'^update/(?P<uuid>[\w-]+)/$', server_update_all, name='server_update_all'),
	url(r'^change/auto/(?P<uuid>[\w-]+)/$', server_change_auto_updates, name='server_change_auto_updates'),
	url(r'^change/interval/(?P<uuid>[\w-]+)/$', server_change_update_interval,
														name='server_change_update_interval'),

	url(r'^package/ignore/(?P<package_id>\d+)/$', package_change_ignore, name='package_change_ignore'),
	url(r'^package/update/(?P<uuid>[\w-]+)/(?P<package_name>[:+\w\._-]+)/$', package_manual_update, name='package_manual_update'),
	url(r'^status/(?P<uuid>[\w-]+)/$', check_server_status, name='check_server_status'),
]
