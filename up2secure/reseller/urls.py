from django.conf.urls import url

from .views import ResellerListView

urlpatterns = [
	url(r'^$', ResellerListView.as_view(), name='reseller_list'),
]