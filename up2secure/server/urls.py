from django.conf.urls import url

from .views import ServerListView

urlpatterns = [
	url(r'^$', ServerListView.as_view(), name='server_list'),
]